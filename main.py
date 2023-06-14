# -*- coding: utf-8 -*-
"""
Created on Tue May  9 12:01:29 2023

@author: tmuenker
"""

import PySimpleGUI as sg
import nidaqmx
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from configparser import ConfigParser


import waveform_builder
import wave_form_builder_daniel
from save_to_db import ArrayDatabase
from trajectory_builder import TrajectoryBuilder

#%%

class mlp_figure:
    
    def __init__(self,gui,canvas,title="Current Output"):
        
        plt.ioff()
        self.title=title
        self.gui=gui
        self.canvas=canvas
        self.fig, self.ax = plt.subplots(figsize=(4,2))
        self.ax.plot([0,0])
        self.ax.set_xlabel("Time[s]")
        self.ax.set_ylabel("Voltage[V]")
        self.ax.set_title(self.title)
        plt.tight_layout()
        self.figcanvas=FigureCanvasTkAgg(self.fig, gui.window[self.canvas].TKCanvas)
        self.draw_to_canvas([0,1], [0,0])
        
        

    def draw_to_canvas(self,t,waveform):
        # Embed the figure canvas in the PySimpleGUI window

        self.ax.clear()
        self.ax.set_xlabel("Time[s]")
        self.ax.set_ylabel("Voltage[V]")
        self.ax.set_title(self.title)
        
        self.ax.plot(t,waveform,'k-')
        plt.tight_layout()
        self.figcanvas.draw()
        self.figcanvas.get_tk_widget().pack(fill="both", expand=True)
        
        

class StimulationApp:
    
    
    
    def __init__(self):
        '''Close all old figures'''
        plt.close('all')
        
        '''Define some propertis'''
        #Import/Init database
        self.db=ArrayDatabase('Waveforms.db')
        #Sample rate
        self.sample_rate=5000
        #Current nidaqmx task
        self.task = None
        #Bipolar stimulation?
        self.bipolar=True
        # Define a flag to indicate if the output is currently active
        self.output_active = False
        #Default name of config file
        self.config_name= "USERSETTINGS" 
        #Waveform
        self.waveform=[0,0]
        self.t=[0,1]
        self.default_channel="?channel"
        self.default_device='?device'
        self.curr_channel="channel"
        self.curr_device='device'
        
        
        # Define the available devices and channels
        self.devices = nidaqmx.system.System.local().devices
        self.device_choices = [device.name for device in self.devices]
        self.device = nidaqmx.system.Device(self.device_choices[0])
        self.device.reset_device()
        self.channel_choices = [f"ao{i}" for i in range(len(self.device.ao_physical_chans))]
        
        
        
        # Define the GUI layout        
        self.layout=self.get_layout()
        
        #Create the main window
        self.window = sg.Window("Analog Output Controller", self.layout ,resizable=True,finalize=True)
        self.window.bring_to_front()
        
        # Create matlab figures and display them
        self.preview_figure=mlp_figure(self, "-CANVAS2-",title='Preview output')
        self.output_figure=mlp_figure(self, "-CANVAS-",title='Current output')
        
    
        
        
        
        
        
        
        
        
    def run(self):
        
        self.t0=time.time()
        # Event loop to process events and update the GUI
        self.event, self.values = self.window.read(10)
        self.load_config()
        while True:
            self.event, self.values = self.window.read(10)
            
            if self.event == sg.WIN_CLOSED:
                print('closed')
                self.save_config()
                try:
                    
                    self.task.stop()
                    self.waveform=[0,0]
                    self.task.write(self.waveform)
                    self.task.start()
                    self.task.stop()
                    self.task.close()
                    
                except:
                    pass
                break
            
            if self.event == '-SAVE-':
                self.db.gui_save(self.t, self.waveform)
            
            if self.event == "-DEVICE-":
                # Update the available channels when a new device is selected
                self.device = nidaqmx.system.Device(self.values["-DEVICE-"])
                self.device.reset_device()
                self.channel_choices = [f"ao{i}" for i in range(len(self.device.ao_physical_chans))]
                self.window["-CHANNEL-"].update(values=self.channel_choices)
                self.curr_device=self.values['-DEVICE-']
            
            if self.event=='-CHANNEL-':
                self.curr_channel=self.values['-CHANNEL-']
            
            if self.event == "-START-":
                self.start_output()
                self.start_time=time.time() 
                
            if self.event == "-STOP-":
                self.stop_output()
                
            if self.event == "-BIORUNI-":
                if self.values["-BIORUNI-"] == 'bipolar':
                    self.bipolar=True
                else:
                    self.bipolar=False
                    
            if self.event == "-GENERATE-":
                wb=waveform_builder.showck_waveform_builder(self.sample_rate)
                t,waveform=wb.run()
                if t is not None:
                    self.t,self.waveform=t,waveform
                self.preview_figure.draw_to_canvas(self.t, self.waveform)
                 
            if self.event == "-DANIEL-":
                wb=wave_form_builder_daniel.waveform_daniel(self.sample_rate)
                res=wb.run()
                if res!= None:
                    t,waveform=res
                    self.t,self.waveform=t,waveform
                self.preview_figure.draw_to_canvas(self.t, self.waveform)
                
            if self.event =="-LOAD_DB-":
                result=self.db.gui_load()
                if result!=None:
                    self.t,self.waveform=result
                    self.preview_figure.draw_to_canvas(self.t, self.waveform)
                    
            if self.event=="-DELETE_DB-":
                self.db.gui_delete()
                
            if self.event == 'Trajectory builder':
                tb=TrajectoryBuilder(self.sample_rate)
                result = tb.run()
                if result!=None:
                    self.t,self.waveform=result
                    self.preview_figure.draw_to_canvas(self.t, self.waveform)
                
                
                    
                    
            if self.event == '-LOADSETTINGS-':
                self.load_settings()
               
            if self.output_active:
                
                if self.window['-STOP_AFTER_TIME-'].get()==True:
                    
                    if (time.time()-self.start_time)>float(self.window['-DURATION-'].get().replace(",", ".")):
                        print('Duration ended')
                        self.stop_output()

        # Close the window
        self.window.close()
        
        
        
        
    def get_layout(self):
        sg.theme('TealMono')


        



        layout= [  
            [sg.Text("Hardware settings:", relief="raised", border_width=5,expand_x=True, justification='center')],
            [sg.Text("Select device:"),sg.Combo(self.device_choices,default_value=self.device_choices[0], key="-DEVICE-", enable_events=True),
            sg.Text("Select channel:"),sg.Combo(self.channel_choices,default_value=self.channel_choices[0], key="-CHANNEL-", enable_events=True,size=(10,5))],

            
            [sg.Text("Set Pulse shape", relief="raised", border_width=5,expand_x=True, justification='center')],
            [sg.Button('Generate simple pulse',key="-GENERATE-"),sg.Button('Generate Pulse "Daniel"',key="-DANIEL-"),sg.Button('Pulse Generator',key='Trajectory builder')],
            
            [sg.Text("Save or load Pulses", relief="raised", border_width=5,expand_x=True, justification='center')],
            [sg.Button('Save current pulse to database', key='-SAVE-', enable_events=True),sg.Button('Load pulse from database',key="-LOAD_DB-"),sg.Button('Delte pulse from database',key="-DELETE_DB-")],
            
            [sg.Text("Start Stimulation", relief="raised", border_width=5,expand_x=True, justification='center')],
            [sg.Checkbox('Stop signal after time?',key='-STOP_AFTER_TIME-'),sg.Text("Duration [s]:"),sg.InputText("5", key="-DURATION-",size=(10,5), enable_events=True)],
            [sg.Button(key='-START-', enable_events=True,image_filename='button_images/start_button.png',button_color=()), sg.Button(key='-STOP-',disabled=True, enable_events=True,image_filename='button_images/stop_button.png',button_color=())],
            
            [sg.Text("Current Voltage", relief="raised", border_width=5,expand_x=True, justification='center')],
            [sg.Canvas(key="-CANVAS2-"),sg.Canvas(key="-CANVAS-")]
        ]




        return layout
    
    
    def save_config(self):
        print('Save config')
        config_name=self.config_name

        config_object = ConfigParser()
        config_object.read("config.ini")
        config_object[config_name] = {
            "device": str(self.curr_device),
            "channel": str(self.curr_channel),
        }
        #Write the above sections to config.ini file
        with open('config.ini', 'w') as conf:
            config_object.write(conf)
            print('config saved')
            
    def load_config(self):
        self.window
        config_name=self.config_name
        config_object = ConfigParser()
        try:
            config_object.read("config.ini")
            settings= config_object[config_name]
    
            self.default_device=settings['device']
            self.default_channel=settings['channel']
            print('load config')
        except:
            print('Couldn load settings')
            
        self.window['-CHANNEL-'].update(value=self.default_channel)
        self.window['-DEVICE-'].update(value=self.default_device)

        self.window.refresh()
        
            
    def start_output(self):
        print('"start_output", get waveform and start "output_waveform"')
        try:
            
            self.output_waveform()
            self.output_active=True
        except Exception as inst:
            print(type(inst))    # the exception type
            print(inst.args)     # arguments stored in .args
            print(inst)  
            sg.popup_error('Could not start output', title='Error')
            print()
            try:
                self.task.close()
            except:
                pass
            self.window.close()
            
    def stop_output(self):
        print('"stop_output", sets waveform to 0')
        self.task.stop()
        waveform=[0,0,0]
        t=[0,0.5,1]
        self.task.write(waveform)
        self.task.start()
        self.task.stop()
        
        self.output_figure.draw_to_canvas(t,waveform)
        
        self.window['-START-'].update(disabled=False)
        self.window['-STOP-'].update(disabled=True)
        
        self.output_active=False
            
    def output_waveform(self):

        print('"output_waveform", starts writing waveform')
        if self.task == None:
            self.task=nidaqmx.Task()
            self.task.ao_channels.add_ao_voltage_chan(
                f"{self.window['-DEVICE-'].get()}/{self.window['-CHANNEL-'].get()}"
            )
            self.task.timing.cfg_samp_clk_timing(rate=self.sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        
        print(self.waveform)
        self.task.write(self.waveform)
        self.task.start()
        self.output_figure.draw_to_canvas(self.t,self.waveform)
        
        self.window['-START-'].update(disabled=True)
        self.window['-STOP-'].update(disabled=False)
        
    def get_waveform(self):
        """
        Reads the current settings in the gui and returns a waveform acccording to these settings.

        Returns
        -------
        time array, voltage array

        """
        amplitude = float(self.values['-AMPLITUDE-'])
        stimulation = float(self.window["-STIMULATION-"].get())
        repitition = float(self.window["-REPITITION-"].get())
        
        N=int(self.sample_rate*repitition)
        
        self.waveform=np.zeros(N)
        signal_end=int(stimulation*self.sample_rate)
        self.t=np.linspace(0,repitition-1/self.sample_rate,N)
        self.waveform[:signal_end]=amplitude
        if self.bipolar:
            self.waveform[int(signal_end/2):signal_end]=-amplitude
        
        return(self.t,self.waveform)
    

            

        
if __name__ == '__main__':
    gui = StimulationApp()
    gui.run()


    
        