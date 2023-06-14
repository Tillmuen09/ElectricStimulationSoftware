import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np






class TrajectoryBuilder:
    def __init__(self,sample_rate):
        plt.ioff()
        # Initialize the trajectory
        self.sample_rate=sample_rate
        self.trajectory = []

        # Create the main window
        self.layout = [
            [sg.Text('Click a button to add an array to the trajectory:')],
            [sg.Button('Add Delay'), sg.Button('Add Unipolar'), sg.Button('Add Bipolar')],
            [sg.Text('Trajectory plot:')],
            [sg.Canvas(key='-CANVAS-')],
            [sg.Button('Remove last element'), sg.Button('Clear trajectory'),sg.Button('OK'), sg.Button('Exit')],
        ]
        self.window = sg.Window('Trajectory Viewer', self.layout,finalize=True)

        # Create the plot
        self.fig, self.ax = plt.subplots(figsize=(3,2))
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel('Volatege')
        self.ax.set_xlim([0, 10])
        self.ax.set_ylim([0, 10])
        plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window['-CANVAS-'].TKCanvas)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    def run(self):
        # Start the event loop
        while True:
            # Wait for an event to happen
            event, values = self.window.read()

            # Handle events
            if event == sg.WIN_CLOSED or event == 'Exit':
                
                # Close the main window
                self.window.close()
                return None
            
            if event =='OK':
                full_trajectory = np.concatenate(self.trajectory)
                num_elements = len(full_trajectory)
                x = np.arange(num_elements)/self.sample_rate
                self.window.close()
                return(x,full_trajectory)
                
                
                
            
            if  event == 'Add Delay':
                self.get_pause_element()            
            if event == 'Add Unipolar':
                self.get_unipolar_element()
            if event == 'Add Bipolar':
                self.get_bipolar_element()
                
 

            if event == 'Remove last element':
                # Remove the last array from the trajectory and update the plot
                if self.trajectory:
                    self.trajectory.pop()
                    self.update_plot()

            if event == 'Clear trajectory':
                # Clear the trajectory and update the plot
                self.trajectory.clear()
                self.update_plot()

        
        
    def get_pause_element(self):
        spec_layout = [
            [sg.Text('Enter specifications:')],
            [sg.Text('Duration'), sg.InputText('0.1',key='duration')],
            [sg.Button('Add'), sg.Button('Cancel')],
        ]
        spec_window = sg.Window('Array Entry', spec_layout)
        while True:
            # Wait for an event in the array entry window
            spec_event, spec_values = spec_window.read()

            # Handle events in the array entry window
            if spec_event == sg.WIN_CLOSED or spec_event == 'Cancel':
                break
            elif spec_event == 'Add':
                # Generate an array with the specified specifications
                duration= float(spec_values['duration'])

                array = np.zeros(int(duration*self.sample_rate))


                # Add the array to the trajectory and update the plot
                self.trajectory.append(array)
                self.update_plot()

                break

        # Close the array entry window
        spec_window.close()
        
    def get_unipolar_element(self):
        spec_layout = [
            [sg.Text('Enter specifications:')],
            [sg.Text('Voltage'), sg.InputText('5',key='voltage')],
            [sg.Text('Duration'), sg.InputText('0.002',key='duration')],
            [sg.Button('Add'), sg.Button('Cancel')],
        ]
        spec_window = sg.Window('Array Entry', spec_layout)
        while True:
            # Wait for an event in the array entry window
            spec_event, spec_values = spec_window.read()

            # Handle events in the array entry window
            if spec_event == sg.WIN_CLOSED or spec_event == 'Cancel':
                break
            elif spec_event == 'Add':
                # Generate an array with the specified specifications
                duration= float(spec_values['duration'])
                voltage=float(spec_values['voltage'])

                array = np.ones(int(duration*self.sample_rate))*voltage


                # Add the array to the trajectory and update the plot
                self.trajectory.append(array)
                self.update_plot()

                break

        # Close the array entry window
        spec_window.close()
        
    def get_bipolar_element(self):
        spec_layout = [
            [sg.Text('Enter specifications:')],
            [sg.Text('Voltage'), sg.InputText('5',key='voltage')],
            [sg.Text('Duration'), sg.InputText('0.002',key='duration')],
            [sg.Button('Add'), sg.Button('Cancel')],
        ]
        spec_window = sg.Window('Array Entry', spec_layout)
        while True:
            # Wait for an event in the array entry window
            spec_event, spec_values = spec_window.read()

            # Handle events in the array entry window
            if spec_event == sg.WIN_CLOSED or spec_event == 'Cancel':
                break
            elif spec_event == 'Add':
                # Generate an array with the specified specifications
                duration= float(spec_values['duration'])
                voltage=float(spec_values['voltage'])

                array = np.ones(int(duration*self.sample_rate))*voltage
                N=len(array)
                array[int(N/2):]=-1*array[int(N/2):]


                # Add the array to the trajectory and update the plot
                self.trajectory.append(array)
                self.update_plot()

                break

        # Close the array entry window
        spec_window.close()
        
    

    def update_plot(self):
        # Clear the plot
        self.ax.clear()

        # Plot the trajectory
        if self.trajectory:
            full_trajectory = np.concatenate(self.trajectory)
            num_elements = len(full_trajectory)
            x = np.arange(num_elements)/self.sample_rate
            self.ax.plot(x, full_trajectory)

        # Set the plot labels and limits
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel('Volatege')
        if self.trajectory:
            max_value = max(full_trajectory)
            min_value = min(full_trajectory)
            value_range = max_value - min_value
            self.ax.set_ylim([min_value - 0.1*value_range, max_value + 0.1*value_range])

        # Draw the plot
        self.canvas.draw()
        
               
        
if __name__ == '__main__':
    # Create an instance of the TrajectoryPlotter class
    tp = TrajectoryBuilder(5000)

    # Run the GUI
    print(tp.run())
       
