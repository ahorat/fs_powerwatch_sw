import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfilename
from functools import partial
import threading
import time
import serial
import serial.tools.list_ports
import FormatLabel
import tkinter.font as tkf

from collections import namedtuple


def _on_configure(event):
    if (event.widget == root):
        size = event.width/30
        MainFont.configure(size=int(size))
        AvgFont.configure(size=int(size/2.2))
        MaxFont.configure(size=int(size/2.2))
 
def build_data_view(root, ValueStorage, LimitStorage, Fonts):
    Columnspan_large=4
    
    for i in range (1,4*Columnspan_large+1):
        root.grid_columnconfigure(i, weight=1)
    for i in range (3,6):
        root.grid_rowconfigure(i, weight=2) 
    for i in range (6,7):
        root.grid_rowconfigure(i, weight=1) 
        
    
    # Generate Needed Font
    Fonts['MainFont'] = tkf.Font(family="Arial", size=30, weight ="bold")
    Fonts['AvgFont'] = tkf.Font(family="Arial", size=15, underline=1)
    Fonts['MaxFont'] = tkf.Font(family="Arial", size=15, weight ="bold")
    
    Fonts['DetailAvgFont'] = tkf.Font(family="Arial", size=8, underline=1)
    Fonts['DetailFont'] = tkf.Font(family="Arial", size=8)
    Fonts['DetailMaxFont'] = tkf.Font(family="Arial", size=8, weight ="bold")
    
    # Create value storage to format each cell accordingly
    DataValue = namedtuple('DataValue', ["Value", "Format", "Description"])

    ValueStorage ['A_1']          = DataValue(DoubleVar(root, value = 050.25), "{:3.2F} A", "Current L1")
    ValueStorage ['A_2']          = DataValue(DoubleVar(root, value = 090.25), "{:3.2F} A", "Current L2")
    ValueStorage ['A_3']          = DataValue(DoubleVar(root, value = 100.25), "{:3.2F} A", "Current L3")
    ValueStorage ['A_Sum']        = DataValue(DoubleVar(root, value = 123.25), "{:3.2F} A", "Current Sum")
    ValueStorage ['V_1']          = DataValue(DoubleVar(root, value = 125.25), "{:3.2F} V", "Voltage L1")
    ValueStorage ['V_2']          = DataValue(DoubleVar(root, value = 123.25), "{:3.2F} V", "Voltage L2")
    ValueStorage ['V_3']          = DataValue(DoubleVar(root, value = 123.25), "{:3.2F} V", "Voltage L3")
    ValueStorage ['A_N']          = DataValue(DoubleVar(root, value = 123.25), "{:3.2F} A", "Current N")
    ValueStorage ['kW_1']         = DataValue(DoubleVar(root, value = 123.25), "{:3.2F} kW", "Inst. Power Ph 1")
    ValueStorage ['kW_2']         = DataValue(DoubleVar(root, value = 123.25), "{:3.2F} kW", "Inst. Power Ph 2")
    ValueStorage ['kW_3']         = DataValue(DoubleVar(root, value = 123.25), "{:3.2F} kW", "Inst. Power Ph 3")
    ValueStorage ['kW_Sum']       = DataValue(DoubleVar(root, value = 123.25), "{:3.2F} kW", "Inst. Power Sum ")
    ValueStorage ['kW_1_Avg']     = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kW", "Avg Power Ph 1")
    ValueStorage ['kW_1_max']     = DataValue(DoubleVar(root, value = 100.00), "{:3.2F} kW", "Max Power Ph 1")
    ValueStorage ['kW_2_Avg']     = DataValue(DoubleVar(root, value = 000.10), "{:3.2F} kW", "Avg Power Ph 2")
    ValueStorage ['kW_2_max']     = DataValue(DoubleVar(root, value = 200.00), "{:3.2F} kW", "Max Power Ph 2")
    ValueStorage ['kW_3_Avg']     = DataValue(DoubleVar(root, value = 000.20), "{:3.2F} kW", "Avg Power Ph 3")
    ValueStorage ['kW_3_max']     = DataValue(DoubleVar(root, value = 300.00), "{:3.2F} kW", "Max Power Ph 3")
    ValueStorage ['kW_Sum_Avg']   = DataValue(DoubleVar(root, value = 000.30), "{:3.2F} kW", "Avg Power Sum ")
    ValueStorage ['kW_Sum_max']   = DataValue(DoubleVar(root, value = 600.00), "{:3.2F} kW", "Max Power Sum ")
    ValueStorage ['kVA_1']        = DataValue(DoubleVar(root, value = 001.00), "{:3.2F} kVA", "Apparent Power Ph 1")
    ValueStorage ['kVA_1_Avg']    = DataValue(DoubleVar(root, value = 002.00), "{:3.2F} kVA", "Apparent Power Ph 1 Avg")
    ValueStorage ['kVA_1_max']    = DataValue(DoubleVar(root, value = 003.00), "{:3.2F} kVA", "Apparent Power Ph 1 Max")
    ValueStorage ['kVA_2']        = DataValue(DoubleVar(root, value = 004.00), "{:3.2F} kVA", "Apparent Power Ph 2")
    ValueStorage ['kVA_2_Avg']    = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVA", "Apparent Power Ph 2 Avg")
    ValueStorage ['kVA_2_max']    = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVA", "Apparent Power Ph 2 Max")
    ValueStorage ['kVA_3']        = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVA", "Apparent Power Ph 3")
    ValueStorage ['kVA_3_Avg']    = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVA", "Apparent Power Ph 3 Avg")
    ValueStorage ['kVA_3_max']    = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVA", "Apparent Power Ph 3 Max")
    ValueStorage ['kVA_Sum']      = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVA", "Apparent Power Sum ")
    ValueStorage ['kVA_Sum_Avg']  = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVA", "Apparent Power Sum Avg")
    ValueStorage ['kVA_Sum_max']  = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVA", "Apparent Power Sum Max")
    ValueStorage ['kVAr_1']       = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Ph 1")
    ValueStorage ['kVAr_1_Avg']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Ph 1 Avg")
    ValueStorage ['kVAr_1_max']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Ph 1 Max")
    ValueStorage ['kVAr_2']       = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Ph 2")
    ValueStorage ['kVAr_2_Avg']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Ph 2 Avg")
    ValueStorage ['kVAr_2_max']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Ph 2 Max")
    ValueStorage ['kVAr_3']       = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Ph 3")
    ValueStorage ['kVAr_3_Avg']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Ph 3 Avg")
    ValueStorage ['kVAr_3_max']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Ph 3 Max")
    ValueStorage ['kVAr_Sum']     = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Sum ")
    ValueStorage ['kVAr_Sum_Avg'] = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Sum Avg")
    ValueStorage ['kVAr_Sum_max'] = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} kVAr", "Reactive Power Sum Max")
    ValueStorage ['Dist_1']       = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Ph 1")
    ValueStorage ['Dist_1_Avg']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Ph 1 Avg")
    ValueStorage ['Dist_1_max']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Ph 1 Max")
    ValueStorage ['Dist_2']       = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Ph 2")
    ValueStorage ['Dist_2_Avg']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Ph 2 Avg")
    ValueStorage ['Dist_2_max']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Ph 2 Max")
    ValueStorage ['Dist_3']       = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Ph 3")
    ValueStorage ['Dist_3_Avg']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Ph 3 Avg")
    ValueStorage ['Dist_3_max']   = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Ph 3 Max")
    ValueStorage ['Dist_Sum']     = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Sum ")
    ValueStorage ['Dist_Sum_Avg'] = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Sum Avg")
    ValueStorage ['Dist_Sum_max'] = DataValue(DoubleVar(root, value = 000.00), "{:3.2F} %", "Harm Distortion Sum Max")
    
    ValueStorage ['Cos_1']        = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Power Factor Ph 1")
    ValueStorage ['Cos_1_Avg']    = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Power Factor Ph 1 Avg")
    ValueStorage ['Cos_2']        = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Power Factor Ph 2")
    ValueStorage ['Cos_2_Avg']    = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Power Factor Ph 2 Avg")
    ValueStorage ['Cos_3']        = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Power Factor Ph 3")
    ValueStorage ['Cos_3_Avg']    = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Power Factor Ph 3 Avg")
    ValueStorage ['Cos_Sum']      = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Power Factor Sum")
    ValueStorage ['Cos_Sum_Avg']  = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Power Factor Sum Avg")
    
    ValueStorage ['V_12']         = DataValue(DoubleVar(root, value = 0.00), "{:3.2F} V", "Voltage 1-2")
    ValueStorage ['V_23']         = DataValue(DoubleVar(root, value = 0.00), "{:3.2F} V", "Voltage 2-3")
    ValueStorage ['V_31']         = DataValue(DoubleVar(root, value = 0.00), "{:3.2F} V", "Voltage 3-1")
    ValueStorage ['V_Sum']        = DataValue(DoubleVar(root, value = 0.00), "{:3.2F} V", "Voltage Sum")
    ValueStorage ['Tgs_1']        = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Tangens(Phi) Ph 1")
    ValueStorage ['Tgs_2']        = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Tangens(Phi) Ph 2")
    ValueStorage ['Tgs_3']        = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Tangens(Phi) Ph 3")
    ValueStorage ['FREQ']         = DataValue(DoubleVar(root, value = 50.00), "{:2.2F} Hz", "Frequency")
    
    ValueStorage ['kWh_1']        = DataValue(DoubleVar(root, value = 0.00), "{:4.1F} kWh", "Power Cons. Ph 1")
    ValueStorage ['kVArh_1']      = DataValue(DoubleVar(root, value = 0.00), "{:4.1F} kVArh", "Reactive Power Consumption Ph 1")
    ValueStorage ['kWh_2']        = DataValue(DoubleVar(root, value = 0.00), "{:4.1F} kWh", "Power Cons. Ph 2")
    ValueStorage ['kVArh_2']      = DataValue(DoubleVar(root, value = 0.00), "{:4.1F} kVArh", "Reactive Power Consumption Ph 2")
    ValueStorage ['kWh_3']        = DataValue(DoubleVar(root, value = 0.00), "{:4.1F} kWh", "Power Cons. Ph 3")
    ValueStorage ['kVArh_3']      = DataValue(DoubleVar(root, value = 0.00), "{:4.1F} kVArh", "Reactive Power Consumption Ph 3")
    ValueStorage ['kWh_Sum']      = DataValue(DoubleVar(root, value = 0.00), "{:4.1F} kWh", "Power Cons. Sum")
    ValueStorage ['kVArh_Sum']    = DataValue(DoubleVar(root, value = 0.00), "{:4.1F} kVArh", "Reactive Power Consumption Sum")
    
    # Unused    
    ValueStorage ['Tgs_Sum']      = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Tangens(Phi) Sum")
    ValueStorage ['AUX']          = DataValue(DoubleVar(root, value = 0.00), "{:1.3F}", "Auxiliary Value")
    
    LimitStorage['A_1']            =  [100, 120]
    LimitStorage['A_2']            =  [100, 120]
    LimitStorage['A_3']            =  [100, 120]
    LimitStorage['A_Sum']          =  [300, 375]
    LimitStorage['V_1']            =  [0, 0]
    LimitStorage['V_2']            =  [0, 0]
    LimitStorage['V_3']            =  [0, 0]
    LimitStorage['A_N']            =  [100, 120]
    LimitStorage['kW_1']           =  [120, 145]
    LimitStorage['kW_2']           =  [120, 145]
    LimitStorage['kW_3']           =  [120, 145]
    LimitStorage['kW_Sum']         =  [120, 145]
    
    
    ## Top 3 Rows reserved for later usage
    
    Columnspan_large=4
    # Recent Current, Voltage and Power Values Values
    for valueIndex in range(0,12):
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[valueIndex]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[valueIndex]].Format, 
            limits=LimitStorage[list(ValueStorage.keys())[valueIndex]], 
            font = Fonts['MainFont'])
        label.grid(row=int(valueIndex/4+3), columnspan=Columnspan_large, 
            column=int((Columnspan_large*valueIndex)%16+1), padx=5, pady=5, sticky='NSWE');
    
    #AVG Power
    for valueIndex in range(0,4):
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[2*valueIndex+12]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[2*valueIndex+12]].Format, 
            font = Fonts['AvgFont'])
        label.grid(row=6, columnspan=int(Columnspan_large/2), 
            column=int(Columnspan_large*valueIndex+1), padx=5, pady=5, sticky='WE');
            
    #Max Power
    for valueIndex in range(0,4):
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[2*valueIndex+13]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[2*valueIndex+13]].Format, font = Fonts['MaxFont'], foreground = "red")
        label.grid(row=6, columnspan=int(Columnspan_large/2), column=int(Columnspan_large*valueIndex+3), padx=5, pady=5, sticky='WE');
    
    
    # Row 6 reserved
    # Power and Distortion Values
    id_offset=20
    row_offset = 7
    for valueIndex in range(0,12):
        label = tk.Label(root, text=ValueStorage[list(ValueStorage.keys())[3*valueIndex+id_offset]].Description, 
            font=Fonts['DetailFont'])
        label.grid(row=int(row_offset+((valueIndex)/4)), column=int((4*valueIndex)%16+1), padx=5, pady=5, sticky='W')
        
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[3*valueIndex+id_offset]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[3*valueIndex+id_offset]].Format, font=Fonts['DetailFont'])
        label.grid(row=int(row_offset+(valueIndex/4)), column=int((4*valueIndex+1)%16+1), padx=5, pady=5, sticky='WE')
        
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[3*valueIndex+id_offset+1]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[3*valueIndex+id_offset+1]].Format, font=Fonts['DetailAvgFont'])
        label.grid(row=int(row_offset+(valueIndex/4)), column=int((4*valueIndex+2)%16+1), padx=5, pady=5, sticky='WE')
        
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[3*valueIndex+id_offset+2]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[3*valueIndex+id_offset+2]].Format, font=Fonts['DetailMaxFont'], foreground="red")
        label.grid(row=int(row_offset+(valueIndex/4)), column=int((4*valueIndex+3)%16+1), padx=5, pady=5, sticky='WE')
    
    
    # Cosine
    id_offset=56
    row_offset = 10
    for valueIndex in range(0,4):
        label = tk.Label(root, text=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset]].Description, 
            font=Fonts['DetailFont'])
        label.grid(row=int(row_offset+((valueIndex)/4)), columnspan=2, column=int((4*valueIndex)%16+1), padx=5, pady=5, sticky='W');
        
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset]].Format, font=Fonts['DetailFont'])
        label.grid(row=int(row_offset+(valueIndex/4)), column=int((4*valueIndex+1)%16+1), padx=5, pady=5, sticky='WE');
        
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset+1]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset+1]].Format, font=Fonts['DetailAvgFont'])
        label.grid(row=int(row_offset+(valueIndex/4)), column=int((4*valueIndex+2)%16+1), padx=5, pady=5, sticky='WE');
         
       
        
    # Voltage and Tangens
    id_offset=64
    row_offset = 11
    for valueIndex in range(0,8):
        label = tk.Label(root, text=ValueStorage[list(ValueStorage.keys())[valueIndex+id_offset]].Description, 
            font=Fonts['DetailFont'])
        label.grid(row=int(row_offset+((valueIndex)/8)), column=int((2*valueIndex)%16+1), padx=5, pady=5, sticky='W');
        
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[valueIndex+id_offset]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[valueIndex+id_offset]].Format, font=Fonts['DetailFont'])
        label.grid(row=int(row_offset+(valueIndex/8)), column=int((2*valueIndex+1)%16+1), padx=5, pady=5, sticky='WE');


    # Power Consumption
    id_offset=72
    row_offset = 13
    for valueIndex in range(0,4):
        label = tk.Label(root, text=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset]].Description, 
            font=Fonts['DetailMaxFont'])
        label.grid(row=int(row_offset+((valueIndex)/4)), columnspan=2, column=int((4*valueIndex)%16+1), padx=5, pady=5, sticky='W');
        
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset]].Format, font=Fonts['DetailMaxFont'])
        label.grid(row=int(row_offset+(valueIndex/4)), columnspan=2, column=int((4*valueIndex+1)%16+1), padx=5, pady=5, sticky='WE')
        
        label = FormatLabel.FormatLabel(root, textvariable=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset+1]].Value, 
            format=ValueStorage[list(ValueStorage.keys())[2*valueIndex+id_offset+1]].Format, font=Fonts['DetailMaxFont'])
        label.grid(row=int(row_offset+(valueIndex/4)), column=int((4*valueIndex+3)%16+1), padx=5, pady=5, sticky='WE');
    
