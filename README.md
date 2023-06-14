# Electric Stimulation Software

This is a graphical user interface (GUI) for controlling analog output stimulation using the Analog Output (AO) channels of a National Instruments Data Acquisition (NI-DAQ) device. The GUI allows you to generate and preview pulse waveforms, save and load waveforms from a database, and start or stop the output stimulation.

## Prerequisites

- Python 3.x
- PySimpleGUI
- nidaqmx
- numpy
- matplotlib

## Installation

1. Make sure you have Python installed on your system.
2. Install the required packages by running the following command:
   ```
   pip install PySimpleGUI nidaqmx numpy matplotlib
   ```

## Usage

### Application example
- Start the software
- Select device and channel 
- Generate the pulse you want to apply:
  - Click Generate simple pulse. A new window will appear.
  - Select if the pulse should be uni or bipolar
  - Chose Amplitude, Stimulation time and repetition time.
    - Stimulation time determines the length of 1 pulse
    - Repetition time determines after what time this pulse is repeated. Frequencie would be 1/repetition time
  -  Press submit to save this pulse
- Using the "Save or load Pulses" buttons, you can save the pulse shape to a database, or load previously saved shapes.
- Select if you want to apply the pulse for a certain amaount of time (check "Stop signal after time") or if you want to end it via button click
- Press start to apply the stimulation and stop to end it


## Database

The GUI provides functionality to save and load pulse waveforms from a database. The waveform data is stored in a SQLite database file named `Waveforms.db`. The `ArrayDatabase` class is used for handling database operations.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [PySimpleGUI](https://pysimplegui.readthedocs.io/)
- [nidaqmx](https://nidaqmx-python.readthedocs.io/)
- [numpy](https://numpy.org/)
- [matplotlib](https://matplotlib.org/)
