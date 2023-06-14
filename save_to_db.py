# -*- coding: utf-8 -*-
"""
Created on Tue May  9 18:20:03 2023

@author: tmuenker
"""

import sqlite3
import numpy as np
import PySimpleGUI as sg
import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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

class ArrayDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS arrays
                          (name text PRIMARY KEY, data blob)''')
        self.conn.commit()
        
    def write_tuple(self, name, array_tuple):
        tuple_bytes = pickle.dumps(array_tuple)
        self.c.execute('INSERT OR REPLACE INTO arrays VALUES (?, ?)', (name, sqlite3.Binary(tuple_bytes)))
        self.conn.commit()
        
    def load_tuple(self, name):
        self.c.execute('SELECT data FROM arrays WHERE name = ?', (name,))
        row = self.c.fetchone()
        if row is None:
            return None
        tuple_bytes = row[0]
        tuple_of_arrays = pickle.loads(tuple_bytes)
        return tuple_of_arrays
    
    def list_arrays(self):
        self.c.execute('SELECT name FROM arrays')
        return [str(row[0]) for row in self.c.fetchall()]
    
    
    def gui_load(self):
        layout=[
            [sg.Text('Available arrays:'), sg.Combo(self.list_arrays(), key='available_arrays',enable_events=True)],
            [sg.Canvas(key='Canvas')],
            [sg.Button('Load Available Array'), sg.Exit()]
            ]
        self.window=sg.Window('Load Waveform', layout,finalize=True)
        preview_figure=mlp_figure(self, "Canvas",title='Pulse')
        self.t=[0,1]
        self.waveform=[1,1]
        preview_figure.draw_to_canvas(self.t, self.waveform)
        
        while True:
            event, values = self.window.read()
            print(event)
            if event == sg.WIN_CLOSED or event == 'Exit':
                self.window.close()
                return(None)
            
            if event == 'available_arrays':
                print('selcted')
                name = values['available_arrays']
                array = self.load_tuple(name)
                if array != None:
                    self.t,self.waveform = array
                    preview_figure.draw_to_canvas(self.t,self.waveform)
                
            
            elif event == 'Load Available Array':
                # load the selected available array from the database and display it
                name = values['available_arrays']
                array = self.load_tuple(name)
                self.window.close()
                return(array)
            
    def gui_save(self,t,waveform):
        layout=[
            [sg.Text('Name: '), sg.InputText(key='name')],
            [sg.Button('Save')]
            ]
        window=sg.Window('Save Waveform', layout)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                window.close()
                return(None)
            elif event == 'Save':
                # parse the input array string and write the array to the database
                name = values['name']
                array=(t,waveform)
                window.close()
                self.write_tuple(name, array)
                
    def delete_array(self, name):
        self.c.execute('DELETE FROM arrays WHERE name = ?', (name,))
        self.conn.commit()
                
    def gui_delete(self):
        layout = [
            [sg.Text('Select an array to delete:'), sg.Combo(self.list_arrays(), key='available_arrays',enable_events=True)],
            [sg.Button('Delete Array'), sg.Exit()]
        ]
        window = sg.Window('Delete Array', layout)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                window.close()
                return

            elif event == 'Delete Array':
                # load the selected available array from the database and display it
                name = values['available_arrays']
                array = self.load_tuple(name)
                if array is not None:
                    fig, ax = plt.subplots()
                    ax.plot(array[0], array[1])
                    ax.set_title(f'Array: {name}')
                    plt.show(block=False)
                    confirm_layout = [[sg.Text(f'Are you sure you want to delete {name}?')],
                                      [sg.Button('Yes'), sg.Button('No')]]
                    confirm_window = sg.Window('Confirm Deletion', confirm_layout)
                    confirm_event, confirm_values = confirm_window.read()
                    confirm_window.close()
                    if confirm_event == 'Yes':
                        self.delete_array(name)
                        sg.Popup(f'{name} deleted successfully!')
                    else:
                        sg.Popup(f'{name} not deleted.')
                    plt.close(fig)
                else:
                    sg.Popup(f'{name} not found in the database.')


        

if __name__=="__main__":
    t=[1,2,3,4]
    waveform=[5,5,5,5]
    
    db=ArrayDatabase('Waveforms.db')
    #result=db.gui_save(t,waveform)
    result=db.gui_load()
    #result=db.gui_delete()