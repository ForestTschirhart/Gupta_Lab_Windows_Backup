import os
import time
import matplotlib.pyplot as plt
import numpy as np
from moku.instruments import Datalogger, Oscilloscope

# Connect to your Moku by its ip address using Datalogger('192.168.###.###')
# force_connect will overtake an existing connection
#IP_ADDRESS = '192.168.73.1' # if using Wireless need IvP4
IP_ADDRESS = '[fe80::7269:79ff:feb9:630a%6]'  # if using USB-C need IPv6
FOLDER_NAME = '5-19'  # Folder to save data files
DURATION = 1 # Log duration in seconds
CHANNELS = 2  # Number of channels to log need only 1 for max sampling rate 1e6 Hz
TRACE_DURATION = 0.04 # 40 ms example trace


def test_plot(osc):
    try:
        osc.set_frontend(channel=1, impedance='1MOhm', coupling="DC", range="10Vpp")
        osc.set_frontend(channel=2, impedance='1MOhm', coupling="DC", range="10Vpp")
        # Trigger on input Channel 2, rising edge, 0V 
        osc.set_trigger(type='Edge', source='Input2', level=0)
        # View +-10msec, i.e. trigger in the centre
        osc.set_timebase(-TRACE_DURATION/2, TRACE_DURATION/2)
        sample_rate = osc.get_samplerate()
        print(f"Sample rate: {sample_rate}")
        osc.set_source(1, 'Input1')
        osc.set_source(2, 'Input2')
        data = osc.get_data()
        # Set up the plotting parameters
        plt.ion()
        plt.show()
        plt.grid(visible=True)
        plt.ylim([-0.3, 0.3])
        plt.xlim([data['time'][0], data['time'][-1]])
        line1, = plt.plot([])
        line2, = plt.plot([])
        # Configure labels for axes
        ax = plt.gca()
        # This loops continuously updates the plot with new data 
        # also saves data at specific intervals
        while True:
            # Get new data
            data = osc.get_data()
            # Update the plot
            line1.set_ydata(np.array(data['ch1'])+0.2)
            line2.set_ydata(np.array(data['ch2'])/20)
            line1.set_xdata(data['time'])
            line2.set_xdata(data['time'])
            plt.pause(0.01)
            
    except KeyboardInterrupt:
        print("Loop exited by user.")
    finally:
        # Close the connection to the Moku device
        # This ensures network resources and released correctly
        osc.relinquish_ownership()

osc = Oscilloscope(IP_ADDRESS, force_connect=True)
test_plot(osc)
osc.relinquish_ownership()

i = Datalogger(IP_ADDRESS, force_connect=True)

try:
    # Configure the frontend
    if CHANNELS == 1: # for max sampling have to explicitly turn off ch2
        i.enable_input(1, enable=True)
        i.enable_input(2, enable=False)   
        i.set_samplerate(1e6)
        i.set_frontend(channel=1, impedance='1MOhm', coupling="DC", range="10Vpp")

    elif CHANNELS == 2:
        i.enable_input(1, enable=True)
        i.enable_input(2, enable=True)
        i.set_samplerate(5e5)
        i.set_frontend(channel=1, impedance='1MOhm', coupling="DC", range="10Vpp")
        i.set_frontend(channel=2, impedance='1MOhm', coupling="DC", range="10Vpp")

    i.set_acquisition_mode(mode='Normal')

    
    # start logging
    logFile = i.start_logging(duration=DURATION)

    # Define the folder where the data files will be saved
    output_folder = os.path.join(os.getcwd(), f"{FOLDER_NAME}")
    os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist

    # Download log from Moku, use liconverter GUI to convert this .li file to whatever you want
    i.download("persist", logFile['file_name'], os.path.join(output_folder, logFile['file_name']))
    print(f"Downloaded log file to {output_folder}.")
    print("Finished Data Run")

except Exception as e:
    i.relinquish_ownership()
    raise e
finally:
    # Close the connection to the Moku device
    # This ensures network resources and released correctly
    i.relinquish_ownership()
    
    
