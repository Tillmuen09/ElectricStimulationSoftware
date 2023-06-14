# -*- coding: utf-8 -*-
"""
Created on Tue May  9 17:34:31 2023

@author: tmuenker
"""

import numpy as np
import PySimpleGUI as sg
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


class waveform_daniel:
  
    def __init__(self,sample_rate):
        
    
        layout = [
            [sg.Text('Frequency (Hz)'), sg.Input('440', key='freq')],
            [sg.Text('Amplitude 1 (V)'), sg.Input('1', key='amp1')],
            [sg.Text('Duration 1 (s)'), sg.Input('1', key='dur1')],
            [sg.Text('Delay (s)'), sg.Input('0', key='delay')],
            [sg.Text('Amplitude 2 (V)'), sg.Input('0.5', key='amp2')],
            [sg.Text('Duration 2 (s)'), sg.Input('0.5', key='dur2')],
            [sg.Text('Number of 2nd pulses'), sg.Input('3', key='num2')],
            [sg.Button('Generate waveform'),sg.Button('Generate preview')],
            [sg.Canvas(key="-CANVAS-")]
        ]
        
        self.sample_rate=sample_rate
        self.dt=1/sample_rate
        # Define the GUI layout        
        #Create the main window
        self.window = sg.Window("Analog Output Controller", layout ,resizable=True,finalize=True)
        self.window.bring_to_front()
        self.preview_figure=mlp_figure(self, "-CANVAS-",title='Preview output')
        
        
    def create_pulse(self,freq, dt, amp_1, duration_1, delay, amp_2, duration_2, number_2, plot=False):

        import matplotlib.pyplot as plt
        """
        Function to create single pulse time series (time, voltage) for CCM (cardiac contractility modulation)

        See https://www.frontiersin.org/articles/10.3389/fphys.2022.1023563

        Parameter
        ---------------------

        freq : float
            Frequency in Hz, determines length of single pulse
        dt : float
            Sampling rate in milliseconds
        amp_1 : float
            Voltagge amplitude of first pulse in Volt
        duration_1 : float
            Duration of first pulse in milliseconds
        delay : float
            Delay between first and second pulse in milliseconds
        amp_2 : float
            Voltage amplitude of second pulses in Volt
        duration_2 : float
            Total duration of second pulse in milliseconds
        number_2 : int
            Number of repetitions in second pulse
            


        Output
        --------------------

        time : ndarray
            Array with list of time points in milliseconds
        pulse : ndarray
            Array with list of voltages in Volt
        """
        
        
        # create time series
        time = np.arange(0, 1 / freq * 1000, dt)
        pulse = np.zeros_like(time)

        # first pulse
        _duration_1 = int(duration_1 / dt)
        pulse[1:_duration_1 + 1] = amp_1

        # second pulse
        _delay = _duration_1 + int(delay / dt)
        _duration_2 = int(duration_2 / dt)
        _rect = int(_duration_2 / 2 / number_2)
        for i in range(2 * number_2):

            if i % 2 == 0:
                pulse[_delay + i * _rect:_delay + (i + 1) * _rect] = amp_2
            else:
                pulse[_delay + i * _rect:_delay + (i + 1) * _rect] = - amp_2

        if plot:
            plt.ion()
            fig, ax = plt.subplots(figsize=(4, 2), layout='constrained')
            ax.plot(time, pulse, c='k', lw=2)
            ax.set_xlim(0, _duration_1 + _delay + _duration_2 + 50)
            ax.set_xlabel('Time [ms]')
            ax.set_ylabel('Voltage [V]')
            plt.show()

        return time, pulse

    def run(self):
        while True:
            self.event, self.values = self.window.read()
            if self.event == sg.WINDOW_CLOSED:
                break
            
            if self.event == 'Generate preview':
                freq = float(self.values['freq'])
                amp1 = float(self.values['amp1'])
                dur1 = float(self.values['dur1'])
                delay = float(self.values['delay'])
                amp2 = float(self.values['amp2'])
                dur2 = float(self.values['dur2'])
                num2 = int(self.values['num2'])
                t, pulse= self.create_pulse(freq,self.dt, amp1, dur1, delay, amp2, dur2, num2)
                self.preview_figure.draw_to_canvas(t, pulse)
                
            
            
            if self.event == 'Generate waveform':
                freq = float(self.values['freq'])
                amp1 = float(self.values['amp1'])
                dur1 = float(self.values['dur1'])
                delay = float(self.values['delay'])
                amp2 = float(self.values['amp2'])
                dur2 = float(self.values['dur2'])
                num2 = int(self.values['num2'])
                t, pulse= self.create_pulse(freq,self.dt, amp1, dur1, delay, amp2, dur2, num2)
                self.window.close()
                return(t,pulse)

            
        self.window.close()
        
if __name__ =="__main__":
    wf=waveform_daniel(1000)
    print(wf.run())
    