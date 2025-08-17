import os
import time
import argparse
import queue
import logging
import logging.handlers
import threading
import PowerWatchDataStorage
import dataclasses
from dataclasses import fields
import dataclasses
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils


class UMG96RMEInterface:
    _logger = logging.getLogger('UMG96RMEInterface')
    
    _device = None;
    _DataStorage = PowerWatchDataStorage.PowerWatchDataStorage()
    
    _DataQueue = queue.SimpleQueue()
    _ReturnDataRecord  = PowerWatchDataStorage.PowerWatchDataStorage()
    
    _datalogger = logging.getLogger('DataLogger')
    
    _thread = None
    
    def __init__(self, _log_file_name, login_cred):
        '''
        Create new Instance
        '''       
        self._logger.setLevel(logging.INFO)        
        self._setupDataLogger(_log_file_name)
        self._login_cred = login_cred
        
    def _setupDataLogger(self, _log_file_name):
        self._datalogger.setLevel(logging.DEBUG)
        self._datalogger.propagate = False        
        os.makedirs(os.path.dirname(_log_file_name), exist_ok =True)    
        dataLoggerHandler = logging.handlers.TimedRotatingFileHandler(_log_file_name, when='H', interval=1)
        formatter = logging.Formatter('%(message)s')
        dataLoggerHandler.setFormatter(formatter)
        
        self._datalogger.addHandler(dataLoggerHandler)

    def collect_all_measurements(self):
        '''
        Request all measurements 
        '''     
        
        data=self._device.read_input_registers(19000,122)         
        data = utils.word_list_to_long(data)
        
        data_In=self._device.read_input_registers(10085,2)         
        data_In = utils.word_list_to_long(data_In)
        
        self._DataStorage.FREQ          = utils.decode_ieee(data[25])
        self._DataStorage.A_1           = utils.decode_ieee(data[6])
        self._DataStorage.A_2           = utils.decode_ieee(data[7])
        self._DataStorage.A_3           = utils.decode_ieee(data[8])
        self._DataStorage.A_Sum         = utils.decode_ieee(data[9])
        self._DataStorage.A_N           = utils.decode_ieee(data_In[0])
        self._DataStorage.V_1           = utils.decode_ieee(data[0])
        self._DataStorage.V_2           = utils.decode_ieee(data[1])
        self._DataStorage.V_3           = utils.decode_ieee(data[2])
        self._DataStorage.V_Sum         = 0#utils.decode_ieee(data[])/1000.0
        self._DataStorage.V_12          = utils.decode_ieee(data[3])
        self._DataStorage.V_23          = utils.decode_ieee(data[4])
        self._DataStorage.V_31          = utils.decode_ieee(data[5])
        self._DataStorage.kW_1          = utils.decode_ieee(data[10])/1000.0
        self._DataStorage.kW_2          = utils.decode_ieee(data[11])/1000.0
        self._DataStorage.kW_3          = utils.decode_ieee(data[12])/1000.0
        self._DataStorage.kW_Sum        = utils.decode_ieee(data[13])/1000.0            
        self._DataStorage.kVA_1         = utils.decode_ieee(data[14])/1000.0        
        self._DataStorage.kVA_2         = utils.decode_ieee(data[15])/1000.0        
        self._DataStorage.kVA_3         = utils.decode_ieee(data[16])/1000.0        
        self._DataStorage.kVA_Sum       = utils.decode_ieee(data[17])/1000.0            
        self._DataStorage.kVAr_1        = utils.decode_ieee(data[18])/1000.0        
        self._DataStorage.kVAr_2        = utils.decode_ieee(data[19])/1000.0        
        self._DataStorage.kVAr_3        = utils.decode_ieee(data[20])/1000.0        
        self._DataStorage.kVAr_Sum      = utils.decode_ieee(data[21])/1000.0            
        self._DataStorage.Dist_1        = utils.decode_ieee(data[58])        
        self._DataStorage.Dist_2        = utils.decode_ieee(data[59])        
        self._DataStorage.Dist_3        = utils.decode_ieee(data[60])        
        self._DataStorage.Dist_Sum      = 0#utils.decode_ieee(data[61])        
        self._DataStorage.Dist_1_Avg    = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Dist_2_Avg    = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Dist_3_Avg    = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Dist_Sum_Avg  = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Cos_1         = utils.decode_ieee(data[22])        
        self._DataStorage.Cos_2         = utils.decode_ieee(data[23])        
        self._DataStorage.Cos_3         = utils.decode_ieee(data[24])        
        self._DataStorage.Cos_Sum       = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Cos_1_Avg     = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Cos_2_Avg     = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Cos_3_Avg     = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Cos_Sum_Avg   = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Tgs_1         = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Tgs_2         = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Tgs_3         = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Tgs_Sum       = 0#utils.decode_ieee(data[2])        
        self._DataStorage.kWh_1         = utils.decode_ieee(data[27])/1000.0        
        self._DataStorage.kWh_2         = utils.decode_ieee(data[28])/1000.0        
        self._DataStorage.kWh_3         = utils.decode_ieee(data[29])/1000.0        
        self._DataStorage.kWh_Sum       = utils.decode_ieee(data[30])/1000.0        
        self._DataStorage.kVArh_1       = utils.decode_ieee(data[43])/1000.0        
        self._DataStorage.kVArh_2       = utils.decode_ieee(data[44])/1000.0       
        self._DataStorage.kVArh_3       = utils.decode_ieee(data[45])/1000.0         
        self._DataStorage.kVArh_Sum     = utils.decode_ieee(data[46])/1000.0  

   
        data=self._device.read_input_registers(2508,24)        
        data = utils.word_list_to_long(data)  
        self._DataStorage.kW_1_Avg      = utils.decode_ieee(data[0])    /1000.0        
        self._DataStorage.kW_2_Avg      = utils.decode_ieee(data[1])    /1000.0        
        self._DataStorage.kW_3_Avg      = utils.decode_ieee(data[2])    /1000.0        
        self._DataStorage.kW_Sum_Avg    = utils.decode_ieee(data[3])    /1000.0          
        self._DataStorage.kVAr_1_Avg    = utils.decode_ieee(data[4])    /1000.0        
        self._DataStorage.kVAr_2_Avg    = utils.decode_ieee(data[5])    /1000.0        
        self._DataStorage.kVAr_3_Avg    = utils.decode_ieee(data[6])    /1000.0        
        self._DataStorage.kVAr_Sum_Avg  = utils.decode_ieee(data[7])    /1000.0            
        self._DataStorage.kVA_1_Avg     = utils.decode_ieee(data[8])    /1000.0        
        self._DataStorage.kVA_2_Avg     = utils.decode_ieee(data[9])    /1000.0        
        self._DataStorage.kVA_3_Avg     = utils.decode_ieee(data[10])   /1000.0        
        self._DataStorage.kVA_Sum_Avg   = utils.decode_ieee(data[11])   /1000.0 


        data=self._device.read_input_registers(3366,24)        
        data = utils.word_list_to_long(data)               
        self._DataStorage.kW_1_max      = utils.decode_ieee(data[0])    /1000.0       
        self._DataStorage.kW_2_max      = utils.decode_ieee(data[1])    /1000.0       
        self._DataStorage.kW_3_max      = utils.decode_ieee(data[2])    /1000.0       
        self._DataStorage.kW_Sum_max    = utils.decode_ieee(data[3])    /1000.0       
        self._DataStorage.kVAr_1_max    = utils.decode_ieee(data[4])    /1000.0      
        self._DataStorage.kVAr_2_max    = utils.decode_ieee(data[5])    /1000.0       
        self._DataStorage.kVAr_3_max    = utils.decode_ieee(data[6])    /1000.0       
        self._DataStorage.kVAr_Sum_max  = utils.decode_ieee(data[7])    /1000.0       
        self._DataStorage.kVA_1_max     = utils.decode_ieee(data[8])    /1000.0        
        self._DataStorage.kVA_2_max     = utils.decode_ieee(data[9])    /1000.0        
        self._DataStorage.kVA_3_max     = utils.decode_ieee(data[10])   /1000.0        
        self._DataStorage.kVA_Sum_max   = utils.decode_ieee(data[11])   /1000.0 
 
        self._DataStorage.Dist_1_max    = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Dist_2_max    = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Dist_3_max    = 0#utils.decode_ieee(data[2])        
        self._DataStorage.Dist_Sum_max  = 0#utils.decode_ieee(data[2])  
    
    def _RunLoop(self):
        """
        Run the data logger 
        """        
        counter = 0;
        self._datalogger.info(F"TimeStamp, "+', '.join([field.name for field in (fields(self._DataStorage))]))
        self._datalogger.info(F"{time.time_ns()//1_000_000}, "+', '.join(['{:f}'.format(x) for x in list(dataclasses.asdict(self._DataStorage).values())]))
        
        while self._RunActive:            
            time.sleep(0.5)
            try:
                self.collect_all_measurements()
                self._datalogger.info(F"{time.time_ns()//1_000_000}, "+', '.join(['{:f}'.format(x) for x in list(dataclasses.asdict(self._DataStorage).values())]))
                self._DataQueue.put(self._DataStorage)       
            except Exception as e:
                if hasattr(e, 'message'):
                    self._logger.error(e.message)
                else:
                    self._logger.error(e)
            
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
            
    def restart(self):
        '''
        Restart the thread, when it is not running
        '''
        if(self._RunActive ==False) or (self._thread is None) or (not self._thread.is_alive()):
            self.run()
     
    def isConnected(self):
        """
        Returns if shelly is connected is opened
        """
        return self._device is not None
     
    def connect(self, ip_hostname):
        """
        Opens the serial port to the vip system and collects first measurement
        
        port: Serial Port for VIP Sys 
        """
        try:
            self._device = ModbusClient(host=ip_hostname, port=502)
        except ValueError:
            print("Error with host or port params")

        self.collect_all_measurements()

    def disconnect(self):
        """
        closes the serial port
        """
        self.stop()
        self._device = None

    def getData(self):
        '''
        Returns a DataStorage Thread-safe
        '''
        try:
            self._ReturnDataRecord = self._DataQueue.get(False)  
            
        except queue.Empty:
            pass
            
        return self._ReturnDataRecord

        
if __name__ == '__main__': 

    parser = argparse.ArgumentParser(
                    prog='UMG96RME Command Line Interface',
                    description='This tool reads out measurements from the UMG96RME')
                    
    parser.add_argument('port', help="IP Address or Host name"); 
    parser.add_argument('-f', '--logfile', dest="logfile", default="./Data_log.dat", help="Path for the logfile"); 
    args = parser.parse_args()
    
    device = UMG96RMEInterface(args.logfile, 0);
    
    device.connect(args.port)
    
    device.run()
    time.sleep(1)
    data = device.getData()
    device.disconnect()
    
    for field in fields(data):
        print(field.name, getattr(data, field.name))
        
        
