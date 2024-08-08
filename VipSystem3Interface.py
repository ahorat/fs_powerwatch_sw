import os
import serial
import regex
from collections import namedtuple
import time
import argparse
import queue
import logging
import logging.handlers
import threading
import PowerWatchDataStorage
from dataclasses  import fields, asdict



class VipSystem3Interface:
    _logger = logging.getLogger('vip3_interface')
    
    _serialport = None;
    _thread = None
    _DataStorage = PowerWatchDataStorage.PowerWatchDataStorage()
    
    _DataQueue = queue.SimpleQueue()
    _ReturnDataRecord = PowerWatchDataStorage.PowerWatchDataStorage()
    
    _datalogger = logging.getLogger('DataLogger')
    
    _START_SERIAL_INTERFACE_KEY = b'\x1BA\r\n'
    _REQUEST_ALL_MEASUREMENTS = b'\x1BM\r\n'
    
    _MEASURING_PAGE_5_ID = 0x0004
    
    RxDataStruct = namedtuple('RxDataStruct', ['length','address','data','checksum'])
    
    def __init__(self, _log_file_name):
        '''
        Create new Instance
        '''
        self._serialport = serial.Serial(None, 9600, timeout=1, parity=serial.PARITY_EVEN, bytesize=7, stopbits=1, rtscts=True, dsrdtr =True);
        self.buf=bytearray()
        
        self._logger.setLevel(logging.INFO)
        
        self._setupDataLogger(_log_file_name)
        
    def _setupDataLogger(self, _log_file_name):
        self._datalogger.setLevel(logging.DEBUG)

        self._datalogger.propagate = False    
        os.makedirs(os.path.dirname(_log_file_name), exist_ok =True)    
        dataLoggerHandler = logging.handlers.TimedRotatingFileHandler(_log_file_name, when='H', interval=1)
        
        formatter = logging.Formatter('%(message)s')
        dataLoggerHandler.setFormatter(formatter)
        
        self._datalogger.addHandler(dataLoggerHandler)
        
        
    def _MakeCheckedRequest(self, request):
        '''
        Make request and check for correct answer. 
        '''
        self._serialport.write(request);
        self._logger.info(F'<-{str(request)}')
        self._serialport.flush()
        
        response = self._serialport.read_until(expected = '\n', size = 4)        
        self._logger.info(F'->{str(response)}')
        if(response != (request)):
            self._logger.warning('Checked Request failed Received: "'+  str(response) +'" Sent: "' +str(request)+ '"')
            return 1
        return 0
    
    def _StartSerialCommunication(self):
        ''' 
        Start serial communication and 
        '''
        error_counter = 0;
        while(self._MakeCheckedRequest(_START_SERIAL_INTERFACE_KEY)):
            error_counter = error_counter + 1;
            if error_counter > 3:
                self._logger.error('Initial Request ESC A failed.')
                return 1
        
        return 0
        

    
        
    def RequestAllMeasurements(self):
        '''
        Request  all measurements available.
        '''
        self._logger.info('Request all measurements')
        
        self._StartSerialCommunication()
        
        error_counter = 0;
        while(self._MakeCheckedRequest(_REQUEST_ALL_MEASUREMENTS)):
            error_counter = error_counter + 1;
            if error_counter > 3:
                self._logger.error('Request for all Measurements failed.')
                return 2
         
        return 0
        
        
    def RequestMeasurementPage(self, page_nr):
        '''
        Request specific measurement page
        
        page_nr:    Specify page nummer, to be requested.
        '''
        
        if(self._StartSerialCommunication()): 
            return 1

        if(self._MakeCheckedRequest(F'\x1Bm{page_nr:X}\r\n')):
            self._logger.error('Request for measurement page failed.')
            return 2
         
        return 0
    
    def RequestNextPage(self):
        '''
        Send Esc O to request the next page according to the command.
        '''
        NEXT_PAGE_REQUEST = b'\x1BO\r\n'
        self._serialport.write(NEXT_PAGE_REQUEST)
        self._logger.info(F'<-{str(NEXT_PAGE_REQUEST)}')        
        self._serialport.flush()
        self._logger.info('Request next page.')
        
        
    def _fastReadLine(self):
        '''
        Faster implementation of read line function
        '''
        lineBreakIndex = self.buf.find(b'\n')
        if lineBreakIndex >= 0:
            r = self.buf[:lineBreakIndex+1]
            self.buf = self.buf[lineBreakIndex+1:]
            return r
        while True:
            charactersToRead = max(1, min(2048, self._serialport.in_waiting))
            data = self._serialport.read(charactersToRead)
            lineBreakIndex = data.find(b'\n')
            if lineBreakIndex >= 0:
                r = self.buf + data[:lineBreakIndex+1]
                self.buf[0:] = data[lineBreakIndex+1:]
                return r
            else:
                self.buf.extend(data)

    def ReadStringFrame(self):
        '''
        Read STRING Frame from Serial stream, that was previously requested. 
        
        Returns: Tuple of (Status, Data)
        '''
        rx_data = self._fastReadLine().decode('ascii')
        self._logger.info(F'->{str(rx_data.encode("ascii"))}')    
        

        if(rx_data[0] != ':'):
            return 1,None;
            
        rx_data_matched = regex.match(r"(:(\w{2})(\w{4})(\w*))(\w)\r\n", rx_data)
        
        if(rx_data_matched is None):
            self._logger.error("Error, Data not parsed")
            return 2,None;
        
        checksum = sum(rx_data_matched[1].encode('ascii')) & 0xFF
        
        checksum = (checksum & 0xF) ^ (checksum >> 4);
        
        rx_data_fields=RxDataStruct(int(rx_data_matched[2][::-1],16),
         int(rx_data_matched[3][::-1],16),
         bytes.fromhex(rx_data_matched[4][::-1])[::-1],
        int(rx_data_matched[5],16))
        
        if(checksum != rx_data_fields.checksum):
            self._logger.error(F"Checksum Error Expected: 0x{checksum:x} Received: 0x{rx_data_fields.checksum:x}")
            return 3,None;
        
        return 0, rx_data_fields
  

    def collect_all_measurements(self, end_address):
        '''
        Request all measurements 
        
        end_address: defines the last address to read. 0x1000 means all
        '''
        
        status = self.RequestAllMeasurements()
        if(status != 0):
            self._logger.error(F"Request failed with Error 0x{status:x}")
            return 1
        
        while(1):
            self.RequestNextPage()
            status, rx_frame = self.ReadStringFrame()
            if(status == 0):
                self.handle_Frame_M(rx_frame);
                if(rx_frame.address == end_address):
                    break
                
     
    def handle_Frame_M(self,frame):
        '''
        Handle M Frame and decode it.
            
        '''
        if(frame.address == 0x0000):        
           self._DataStorage.FREQ        = int.from_bytes(frame.data[0:2], 'little') * 0.1
           self._DataStorage.A_1         = int.from_bytes(frame.data[2:4], 'little') * pow(10.0, int.from_bytes(frame.data[4:5],'little', signed=True)) 
           self._DataStorage.A_2         = int.from_bytes(frame.data[5:7], 'little') * pow(10.0, int.from_bytes(frame.data[7:8],'little', signed=True))  
           self._DataStorage.A_3         = int.from_bytes(frame.data[8:10], 'little') * pow(10.0, int.from_bytes(frame.data[10:11],'little', signed=True)) 
           self._DataStorage.A_Sum       = int.from_bytes(frame.data[11:13], 'little') * pow(10.0, int.from_bytes(frame.data[13:14],'little', signed=True))  
        elif(frame.address == 0x0001):
           self._DataStorage.A_N         = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)) 
           self._DataStorage.V_1         = int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[5:6],'little', signed=True)) 
           self._DataStorage.V_2         = int.from_bytes(frame.data[6:8], 'little') * pow(10.0, int.from_bytes(frame.data[8:9],'little', signed=True))  
           self._DataStorage.V_3         = int.from_bytes(frame.data[9:11], 'little') * pow(10.0, int.from_bytes(frame.data[11:12],'little', signed=True)) 
           self._DataStorage.V_Sum       = int.from_bytes(frame.data[12:14], 'little') * pow(10.0, int.from_bytes(frame.data[14:15],'little', signed=True))  
        elif(frame.address == 0x0002):
           self._DataStorage.V_12        = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)) 
           self._DataStorage.V_23        = int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)) 
           self._DataStorage.V_31        = int.from_bytes(frame.data[5:7], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True))  
           self._DataStorage.kW_1        = int.from_bytes(frame.data[7:9], 'little') * pow(10.0, int.from_bytes(frame.data[9:10],'little', signed=True)-3)
           self._DataStorage.kW_2        = int.from_bytes(frame.data[10:12], 'little') * pow(10.0, int.from_bytes(frame.data[12:13],'little', signed=True)-3)
        elif(frame.address== 0x0003):
           self._DataStorage.kW_3        = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)-3)
           self._DataStorage.kW_Sum      = int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[5:6],'little', signed=True)-3)
           self._DataStorage.kW_1_Avg    = int.from_bytes(frame.data[6:8], 'little') * pow(10.0, int.from_bytes(frame.data[8:9],'little', signed=True)-3)
           self._DataStorage.kW_2_Avg    = int.from_bytes(frame.data[9:11], 'little') * pow(10.0, int.from_bytes(frame.data[11:12],'little', signed=True)-3)
           self._DataStorage.kW_3_Avg    = int.from_bytes(frame.data[12:14], 'little') * pow(10.0, int.from_bytes(frame.data[14:15],'little', signed=True)-3) 
        elif(frame.address== _MEASURING_PAGE_5_ID):
           self._DataStorage.kW_Sum_Avg  = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)-3)
           self._DataStorage.kVA_1       = int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[5:6],'little', signed=True)-3)
           self._DataStorage.kVA_2       = int.from_bytes(frame.data[6:8], 'little') * pow(10.0, int.from_bytes(frame.data[8:9],'little', signed=True)-3)
           self._DataStorage.kVA_3       = int.from_bytes(frame.data[9:11], 'little') * pow(10.0, int.from_bytes(frame.data[11:12],'little', signed=True)-3)
           self._DataStorage.kVA_Sum     = int.from_bytes(frame.data[12:14], 'little') * pow(10.0, int.from_bytes(frame.data[14:15],'little', signed=True)-3)
        elif(frame.address== 0x0005):
           self._DataStorage.kVA_1_Avg   = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)-3)
           self._DataStorage.kVA_2_Avg   = int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[5:6],'little', signed=True)-3)
           self._DataStorage.kVA_3_Avg   = int.from_bytes(frame.data[6:8], 'little') * pow(10.0, int.from_bytes(frame.data[8:9],'little', signed=True)-3)
           self._DataStorage.kVA_Sum_Avg = int.from_bytes(frame.data[9:11], 'little') * pow(10.0, int.from_bytes(frame.data[11:12],'little', signed=True)-3) 
           self._DataStorage.kVAr_1      = int.from_bytes(frame.data[12:14], 'little') * pow(10.0, int.from_bytes(frame.data[14:15],'little', signed=True)-3)
        elif(frame.address== 0x0006):
           self._DataStorage.kVAr_2      = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)-3)
           self._DataStorage.kVAr_3      = int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[5:6],'little', signed=True)-3)
           self._DataStorage.kVAr_Sum    = int.from_bytes(frame.data[6:8], 'little') * pow(10.0, int.from_bytes(frame.data[8:9],'little', signed=True)-3)
           self._DataStorage.kVAr_1_Avg  = int.from_bytes(frame.data[9:11], 'little') * pow(10.0, int.from_bytes(frame.data[11:12],'little', signed=True)-3)
           self._DataStorage.kVAr_2_Avg  = int.from_bytes(frame.data[12:14], 'little') * pow(10.0, int.from_bytes(frame.data[14:15],'little', signed=True)-3)
        elif(frame.address== 0x0007):
           self._DataStorage.kVAr_3_Avg  = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)-3)
           self._DataStorage.kVAr_Sum_Avg= int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[5:6],'little', signed=True)-3)
           self._DataStorage.Distortion_1      = int.from_bytes(frame.data[6:8], 'little') *  0.01
           self._DataStorage.Distortion_2      = int.from_bytes(frame.data[8:10], 'little') *  0.01
           self._DataStorage.Distortion_3      = int.from_bytes(frame.data[10:12], 'little') * 0.01
           self._DataStorage.Distortion_Sum    = int.from_bytes(frame.data[12:14], 'little') * 0.01
           self._DataStorage.Distortion_1_Avg  = int.from_bytes(frame.data[14:16], 'little') * 0.01
        elif(frame.address== 0x0008):
           self._DataStorage.Distortion_2_Avg  = int.from_bytes(frame.data[0:2], 'little') * 0.01 
           self._DataStorage.Distortion_3_Avg  = int.from_bytes(frame.data[2:4], 'little') * 0.01 
           self._DataStorage.Distortion_Sum_Avg= int.from_bytes(frame.data[4:6], 'little') * 0.01  
           self._DataStorage.Cos_1       = int.from_bytes(frame.data[6:8], 'little') * 0.001
           self._DataStorage.Cos_2       = int.from_bytes(frame.data[8:10], 'little') * 0.001
           self._DataStorage.Cos_3       = int.from_bytes(frame.data[10:12], 'little') * 0.001
           self._DataStorage.Cos_Sum     = int.from_bytes(frame.data[12:14], 'little') * 0.001
           self._DataStorage.Cos_1_Avg   = int.from_bytes(frame.data[14:16], 'little') * 0.001
        elif(frame.address== 0x0009):
           self._DataStorage.Cos_2_Avg   = int.from_bytes(frame.data[0:2], 'little') * 0.001
           self._DataStorage.Cos_3_Avg   = int.from_bytes(frame.data[2:4], 'little') * 0.001
           self._DataStorage.Cos_Sum_Avg = int.from_bytes(frame.data[4:6], 'little') * 0.001 
           self._DataStorage.Tan_1       = int.from_bytes(frame.data[6:9], 'little') 
           self._DataStorage.Tan_2       = int.from_bytes(frame.data[9:12], 'little') 
           self._DataStorage.Tan_3       = int.from_bytes(frame.data[12:15], 'little')
        elif(frame.address== 0x000A):
           self._DataStorage.Tan_Sum     = int.from_bytes(frame.data[0:3], 'little')
           self._DataStorage.kWh_1       = float(frame.data[3:12].decode('ascii'))
        elif(frame.address== 0x000B):
           self._DataStorage.kVArh_1     = float(frame.data[0:9].decode('ascii'))
        elif(frame.address== 0x000C):
           self._DataStorage.kWh_2       = float(frame.data[0:9].decode('ascii'))
        elif(frame.address== 0x000D):
           self._DataStorage.kVArh_2     = float(frame.data[0:9].decode('ascii'))
        elif(frame.address== 0x000E):
           self._DataStorage.kWh_3       = float(frame.data[0:9].decode('ascii'))
        elif(frame.address== 0x000F):
           self._DataStorage.kVArh_3     = float(frame.data[0:9].decode('ascii'))
        elif(frame.address== 0x0010):
           self._DataStorage.kWh_Sum     = float(frame.data[0:9].decode('ascii'))
        elif(frame.address== 0x0011):
           self._DataStorage.kVArh_Sum   = float(frame.data[0:8].decode('ascii'))
           self._DataStorage.AUX         = int.from_bytes(frame.data[9:15], 'little') 
        elif(frame.address== 0x0012):
           self._DataStorage.kW_1_max    = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)-3)
           self._DataStorage.kW_2_max    = int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[5:6],'little', signed=True)-3)
           self._DataStorage.kW_3_max    = int.from_bytes(frame.data[6:8], 'little') * pow(10.0, int.from_bytes(frame.data[8:9],'little', signed=True)-3)
           self._DataStorage.kW_Sum_max  = int.from_bytes(frame.data[9:11], 'little')* pow(10.0, int.from_bytes(frame.data[11:12],'little', signed=True)-3)
        elif(frame.address== 0x0013):
           self._DataStorage.kVA_1_max   = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)-3)
           self._DataStorage.kVA_2_max   = int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[5:6],'little', signed=True)-3)
           self._DataStorage.kVA_3_max   = int.from_bytes(frame.data[6:8], 'little') * pow(10.0, int.from_bytes(frame.data[8:9],'little', signed=True)-3)
           self._DataStorage.kVA_Sum_max = int.from_bytes(frame.data[9:11], 'little') * pow(10.0, int.from_bytes(frame.data[11:12],'little', signed=True)-3)
        elif(frame.address== 0x0014):
           self._DataStorage.kVAr_1_max   = int.from_bytes(frame.data[0:2], 'little') * pow(10.0, int.from_bytes(frame.data[2:3],'little', signed=True)-3)
           self._DataStorage.kVAr_2_max   = int.from_bytes(frame.data[3:5], 'little') * pow(10.0, int.from_bytes(frame.data[5:6],'little', signed=True)-3)
           self._DataStorage.kVAr_3_max   = int.from_bytes(frame.data[6:8], 'little') * pow(10.0, int.from_bytes(frame.data[8:9],'little', signed=True)-3)
           self._DataStorage.kVAr_Sum_max = int.from_bytes(frame.data[9:11], 'little') * pow(10.0, int.from_bytes(frame.data[11:12],'little', signed=True)-3)
        elif(frame.address== 0x0015):
           self._DataStorage.Distortion_1_max   = int.from_bytes(frame.data[0:2], 'little') * 0.01
           self._DataStorage.Distortion_2_max   = int.from_bytes(frame.data[2:4], 'little') * 0.01
           self._DataStorage.Distortion_3_max   = int.from_bytes(frame.data[4:6], 'little') * 0.01
           self._DataStorage.Distortion_Sum_max = int.from_bytes(frame.data[6:8], 'little') * 0.01
        else:
            pass
    
    def _RunLoop(self):
        """
        Run the data logger 
        """
        
        counter = 0;
        self._datalogger.info(F"TimeStamp, "+', '.join(list(fields(self._DataStorage))))
        self._datalogger.info(F"{time.time_ns()//1_000_000}, "+', '.join(['{:f}'.format(x) for x in list(asdict(self._DataStorage).values())]))
        
        while self._RunActive:
            if(counter == 0):
                self.collect_all_measurements(0x1000)
                print("Get all Values")
                counter = 60
            else:
                self.collect_all_measurements(_MEASURING_PAGE_5_ID)
            
            counter = counter - 1
            self._datalogger.info(F"{time.time_ns()}, "+', '.join(['{:f}'.format(x) for x in list(asdict(self._DataStorage).values())]))
            self._DataQueue.put(self._DataStorage)       
            
            
    def run(self):
        '''
        Launch a Thread to collect repetitively all measurements.
        '''
        self._RunActive = True
        # Create and start new Thread, such that GUI does not hang.
        self._thread = threading.Thread(target=self._RunLoop)
        self._thread.start()

    def stop(self):
        '''
        Stop the Permanent Run Loop
        '''
        self._RunActive = False
        if(self._thread is not None):
            self._thread.join()
     
    def isConnected(self):
        """
        Returns if the serial port is opened
        """
        return self._serialport.isOpen()
     
    def connect(self, port):
        """
        Opens the serial port to the vip system and collects first measurement
        
        port: Serial Port for VIP Sys 
        """
        self._serialport.port = port
        self._serialport.open()
        self._serialport.reset_input_buffer()
        self.collect_all_measurements(0x1000)

    def disconnect(self):
        """
        closes the serial port
        """
        if(self.isConnected):
            self.stop()
            self._serialport.close()

    def getData(self):
        '''
        Returns a DataStorage Dictonary Thread-safe
        '''
        try:
            self._ReturnDataRecord = self._DataQueue.get(False)  
            
        except queue.Empty:
            pass
            
        return self._ReturnDataRecord

        
if __name__ == '__main__': 

    parser = argparse.ArgumentParser(
                    prog='VIP System 3 Command Line Interface',
                    description='This tool reads out measurements from the VIP System 3')
                    
    parser.add_argument('COM Port', dest="port", help="COM Port for the Communication. eg. /dev/ttyAMA0 or COM2"); 
    parser.add_argument('-f', '--logfile', dest="logfile", default="Data_log.dat", help="Path for the logfile"); 
    args = parser.parse_args()
    
    vip_system = VipSystem3Interface(args.logfile);
    
    vip_system.connect(args.port)
    
    vip_system.run()
    
    print(vip_system.getData)
    
    vip_system.disconnect()
