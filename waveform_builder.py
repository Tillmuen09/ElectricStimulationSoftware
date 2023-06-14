# -*- coding: utf-8 -*-
"""
Created on Tue May  9 15:11:59 2023

@author: tmuenker
"""

import PySimpleGUI as sg
import nidaqmx
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from configparser import ConfigParser


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

class showck_waveform_builder:
    
    def __init__(self,sample_rate):
        self.sample_rate=sample_rate
        # Define the GUI layout        
        self.layout=self.get_layout()
        #Create the main window
        self.window = sg.Window("Analog Output Controller", self.layout ,resizable=True,finalize=True)
        self.window.bring_to_front()
        self.preview_figure=mlp_figure(self, "-CANVAS-",title='Preview output')
        self.t=[0,1]
        self.waveform=[0,0]
        #Bipolar stimulation?
        self.bipolar=True
        
        
    def run(self):
        
        self.event, self.values = self.window.read(1)
        self.update_waveform()
        # Event loop to process events and update the GUI
        while True:
            #Read events
            self.event, self.values = self.window.read()
            if self.event in (sg.WIN_CLOSED, 'Cancel'):
                return [None,None]
            
            if self.event == "-SUBMIT-":
                self.window.close()
                return([self.t,self.waveform])
            
            if self.event == "-Cancel-":
                self.window.close()
                return([None,None])
            
            
            
            if self.values["-BIORUNI-"] == 'bipolar':
                self.bipolar=True
            else:
                self.bipolar=False
            
            if self.event in ["-BIORUNI-",'-AMPLITUDE-',"-STIMULATION-","-REPITITION-","-DURATION-"]:
                self.update_waveform()
            


        # Close the window
        self.window.close()
        
        
    def get_layout(self):
        sg.theme('Reddit')
        
        waveform_column=[
            [sg.Text("Bipolar or Unipolar?"),sg.Combo(['bipolar','unipolar'],'bipolar', key="-BIORUNI-", enable_events=True)],
            [sg.Text("Amplitude [V]:")],
            [sg.Slider(range=(0, 10), default_value=5,resolution=0.1,enable_events=True,orientation='horizontal', key='-AMPLITUDE-')],
            [sg.Text("Stimulation time [s]:"),sg.InputText("0.01", key="-STIMULATION-",size=(10,5), enable_events=True),sg.Text("Minimum 0.004 s")],
            [sg.Text("Repetition time [s]:"),sg.InputText("2", key="-REPITITION-",size=(10,5), enable_events=True),sg.Text('1Hz',key='-FREQ-')],
            [sg.Button('Submit',key='-SUBMIT-'),sg.Button('Cancel',key='-Cancel-')]
            ]
        
        preview_column=[[sg.Canvas(key="-CANVAS-")]]
        
        return [waveform_column,preview_column]
    
    def update_waveform(self):
        try:
            amplitude = float(self.values['-AMPLITUDE-'])
            stimulation = float(self.window["-STIMULATION-"].get().replace(",", "."))
            repitition = float(self.window["-REPITITION-"].get().replace(",", "."))
            
            
            N=int(self.sample_rate*repitition)
            
            self.waveform=np.zeros(N)
            signal_end=int(stimulation*self.sample_rate)
            self.t=np.linspace(0,repitition-1/self.sample_rate,N)
            self.waveform[:signal_end]=amplitude
            if self.bipolar:
                self.waveform[int(signal_end/2):signal_end]=-amplitude
                
            
            self.preview_figure.draw_to_canvas(self.t, self.waveform)
            return(self.t,self.waveform)
        except:
            return(self.t,self.waveform*0)
    
    
if __name__ == '__main__':
    gui = showck_waveform_builder(1000)
    print(gui.run())