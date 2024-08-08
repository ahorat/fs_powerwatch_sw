import os
import ShellyPy
import requests
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



class ShellyInterface:
    _logger = logging.getLogger('ShellyInterface')
    
    _shelly = None;
    _DataStorage = PowerWatchDataStorage.PowerWatchDataStorage()
    
    _DataQueue = queue.SimpleQueue()
    _ReturnDataRecord = {}
    
    _datalogger = logging.getLogger('DataLogger')
    
    def __init__(self, _log_file_name):
        '''
        Create new Instance
        '''       
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

    def collect_all_measurements(self):
        '''
        Request all measurements 
        '''     
        data=self._shelly.status()["emeters"]
        self._DataStorage.A_1         = data[0]['current']
        self._DataStorage.A_2         = data[1]['current']
        self._DataStorage.A_3         = data[2]['current']
        self._DataStorage.A_Sum       = data[0]['current']+data[1]['current']+data[2]['current']
        self._DataStorage.V_1         = data[0]['voltage']
        self._DataStorage.V_2         = data[1]['voltage']
        self._DataStorage.V_3         = data[2]['voltage']
        self._DataStorage.kW_1        = data[0]['power']
        self._DataStorage.kW_2        = data[1]['power']
        self._DataStorage.kW_3        = data[2]['power']
        self._DataStorage.kW_Sum      = data[0]['power'] + data[1]['power'] + data[2]['power']
        self._DataStorage.Cos_1       = data[0]['pf']
        self._DataStorage.Cos_2       = data[1]['pf']
        self._DataStorage.Cos_3       = data[2]['pf']
        self._DataStorage.kWh_1       = data[0]['total']
        self._DataStorage.kWh_2       = data[1]['total']
        self._DataStorage.kWh_3       = data[2]['total']        
    
    def _RunLoop(self):
        """
        Run the data logger 
        """        
        counter = 0;
        print(self._DataStorage)
        self._datalogger.info(F"TimeStamp, "+', '.join([field.name for field in (fields(self._DataStorage))]))
        self._datalogger.info(F"{time.time_ns()//1_000_000}, "+', '.join(['{:f}'.format(x) for x in list(self._DataStorage.values())]))
        
        while self._RunActive:            
            time.sleep(0.5)
            self.collect_all_measurements()
            self._datalogger.info(F"{time.time_ns()}, "+', '.join(['{:f}'.format(x) for x in list(dataclasses.asdict(self._DataStorage).values())]))
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
        Returns if shelly is connected is opened
        """
        return self._shelly is not None
     
    def connect(self, ip_hostname):
        """
        Opens the serial port to the vip system and collects first measurement
        
        port: Serial Port for VIP Sys 
        """
        
        login_cred={"username": "admin", "password":"admin"}
        self._shelly = ShellyPy.Shelly(ip_hostname) # 
        self.collect_all_measurements()

    def disconnect(self):
        """
        closes the serial port
        """
        self.stop()
        self._shelly = None

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
                    prog='Shelly Command Line Interface',
                    description='This tool reads out measurements from the Shelly 3EM')
                    
    parser.add_argument('port', help="IP Address or Host name"); 
    parser.add_argument('-f', '--logfile', dest="logfile", default="Data_log.dat", help="Path for the logfile"); 
    args = parser.parse_args()
    
    shelly_sys = ShellyInterface(args.logfile);
    
    shelly_sys.connect(args.port)
    
    shelly_sys.run()
    
    print(shelly_sys.getData)
    
    shelly_sys.disconnect()
