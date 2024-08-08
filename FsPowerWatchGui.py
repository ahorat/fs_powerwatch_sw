import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinter.filedialog import askopenfilename
from functools import partial
import threading
import time
import serial
import serial.tools.list_ports
import FormatLabel
import tkinter.font as tkf
import VipSystem3Interface
import ShellyInterface
import FsPowerWatchMainFrame
import LightControl
from dataclasses import asdict
import configparser


class FsPowerWatchGui:    
    _PowerMeter = None
    _LightControl = None
    _SerialPortBox = None
    _SerialPortButton = None
    _Fonts = {}
    _ValueStorage = {}        
    _LimitStorage = {}
    _Credentials = None
    
    def _on_configure(self, event):
        '''Event when window gets resized'''
        if (event.widget == self._root):
            size = event.width/30
            self._Fonts['MainFont'].configure(size=int(size))
            self._Fonts['AvgFont'].configure(size=int(size/2.2))
            self._Fonts['MaxFont'].configure(size=int(size/2.2))
                
    def build_header_frame(self, frame):
        '''Build header Frame, which includes connection control'''
        tk.Label(frame, text="Serial Port: ").pack(side=LEFT, padx=5, pady=5);
        self._SerialPortBox = ttk.Combobox(frame, values=[str(x) for x in list(serial.tools.list_ports.comports())]+[ "shellyem3-C45BBE7989DD"], width=50)
        self._SerialPortBox.current(0)
        self._SerialPortBox.pack(side=LEFT, padx=5, pady=5)
        
        self._SerialPortButton = tk.Button(frame, text="Connect", command=self.ManagePort)
        
        self._SerialPortButton.pack(side=LEFT, padx=5, pady=5)
        
        self._CurrentTimeText = labelText = StringVar()
        self._CurrentTimeLabel = tk.Label(frame, textvariable=self._CurrentTimeText )
        self._CurrentTimeLabel.pack(side=RIGHT, padx=15, pady=5)
        self._CurrentTimeText.set("01.01.0001 00:00")
            
    
    def ManagePort(self):
        '''
        Connect/Disconnect the Serial Device
        '''
        if self._PowerMeter.isConnected():
            self._SerialPortButton["text"] = "Connect"
            self._SerialPortBox.state(['!disabled'])
            self._PowerMeter.stop()
            self._PowerMeter.disconnect()
            
        else:
            try:
                serial_port=self._SerialPortBox.get().split(' ',1)[0]
                if((serial_port[0] == "C" or serial_port[0] == "/") and self._PowerMeter is not VipSystem3Interface.VipSystem3Interface):
                    self._PowerMeter= VipSystem3Interface.VipSystem3Interface(self._config["DEFAULT"]["LogPath"])
                else:
                    self._PowerMeter= ShellyInterface.ShellyInterface(self._config["DEFAULT"]["LogPath"], self._Credentials)        
        
                self._PowerMeter.connect(serial_port)
            except:
                if(self._PowerMeter is VipSystem3Interface.VipSystem3Interface):
                    tk.messagebox.showerror(title="Connection Failed", message="Connection to COM Port failed. Please check if another Tool is connected and retry.")
                else:
                    tk.messagebox.showerror(title="Connection Failed", message="Connection to TCP Target failed. Check connection data.")
            else:
                self._SerialPortButton["text"] = "Disconnect"
                self._SerialPortBox.state(['disabled'])
                self._PowerMeter.run()
    
    def CheckLimits(self):
        '''
        Checks the Limits to afterwards set the traffic light.
        '''
        state = LightControl.STATE_GREEN
        
        for i in range(0,12):
            key= list(self._ValueStorage.keys())[i]
            
            if(self._ValueStorage[key].Value.get() > self._LimitStorage[key][0] and 
                self._LimitStorage[key][0] != 0.0):
                state = LightControl.STATE_ORANGE
            if(self._ValueStorage[key].Value.get() > self._LimitStorage[key][1] and 
                self._LimitStorage[key][1] != 0.0):
                state = LightControl.STATE_RED                
                break
        
        return state
            
    
    
    def UpdateData(self):
        '''
        Checks for available Data from Powermeter and updates the View
        '''  
        self._CurrentTimeText.set(time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime()))
        if(self._PowerMeter is not None):
            NewValue = asdict(self._PowerMeter.getData())
            
            for key in NewValue.keys():
                self._ValueStorage[key].Value.set(NewValue[key])
            
        self._LightControl.SwitchLighState(self.CheckLimits())
        self._root.after(500, self.UpdateData)
        
    def __init__(self):
        self._root = tk.Tk()
        self._root.title("Formula Student Power Watch")
        self._root.geometry("1920x1080") 
        self._root.bind("<Configure>", self._on_configure)       
        
        # Create header Frame
        HeaderFrame = Frame(self._root, height = 100)
        HeaderFrame.pack(side=TOP, fill=X)
        self.build_header_frame(HeaderFrame) 
        
        # Create Main Frame
        DataViewFrame = Frame(self._root)
        DataViewFrame.pack(side=BOTTOM, expand = 1, fill=BOTH, pady = 0, padx = 0)
        FsPowerWatchMainFrame.build_data_view(DataViewFrame, self._ValueStorage, self._LimitStorage, self._Fonts)
        
        self._config = configparser.ConfigParser()
        self._config.read("config.ini")
        
        if("DEFAULT" not in self._config):
            self._config["DEFAULT"] = {}
            
        if("logpath" not in self._config):
            self._config["DEFAULT"]["logpath"] = "./FSG_Log"
        
        # Default is VIP System
        self._PowerMeter= VipSystem3Interface.VipSystem3Interface(self._config["DEFAULT"]["LogPath"])
        if("credentials" in self._config):
            self._Credentials = dict(self._config["credentials"])
           
        if("port" in self._config["DEFAULT"]):
            print(F"Try to autoconnect to " + self._config["DEFAULT"]["port"])
            self._SerialPortBox.set(self._config["DEFAULT"]["port"])
            self.ManagePort()
        
        
        self._LightControl = LightControl.RbPILightControl(self._root)
        self._LightControl.SwitchLighState(LightControl.STATE_GREEN)
        
        
        
        self._root.after(500, self.UpdateData)
        self._root.mainloop()
        
        
        # Clean up
        self._PowerMeter.disconnect()
        self._LightControl.SwitchLighState(LightControl.STATE_OFF)
        with open("config.ini",'w',) as configfile:
            self._config.write(configfile)

if __name__ == "__main__":
    FsPowerWatchGui()
