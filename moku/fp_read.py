
# moku example: Plotting Oscilloscope
#
# This example demonstrates how you can configure the Oscilloscope instrument,
# and view triggered time-voltage data frames in real-time.
#
# (c) Liquid Instruments Pty. Ltd.
#
import numpy as np 
import matplotlib.pyplot as plt
from moku.instruments import Oscilloscope
import time
import csv

def savedata(data, metadata, file_prefix='data', output_dir='C:/Users/foresttschirhart/Documents/Gupta_Lab/4-15/locked'):
    # abs_time = metadata[0]
    # time = metadata[1]
    # sample_rate = metadata[2]

    print(f"Time since start: {metadata[1]} seconds")
    filename = f"{output_dir}/{file_prefix}_{metadata[0]}.csv" #ensures no overwrites using abs_time uniqueness
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # write time stuff and other metadata
        writer.writerow(["Metadata:"])
        writer.writerow([f"Absolute time = {metadata[0]}"])
        writer.writerow([f"Time since start = {metadata[1]} seconds"])
        writer.writerow([f"Sample Rate: {metadata[2]}"])
        writer.writerow([])  # Blank row for separation
        # Write the header (keys of the dictionary)
        writer.writerow(data.keys())
        # Write the rows (transpose the lists using zip)
        writer.writerows(zip(*data.values()))



# Connect to your Moku by its ip address using Oscilloscope('192.168.###.###')
# force_connect will overtake an existing connection
i = Oscilloscope('192.168.73.1', force_connect=True)

try:

    i.set_frontend(channel=1, impedance='1MOhm', coupling="DC", range="10Vpp")
    i.set_frontend(channel=2, impedance='1MOhm', coupling="DC", range="10Vpp")

    # Trigger on input Channel 1, rising edge, 0V 
    i.set_trigger(type='Edge', source='Input2', level=0)

    # View +-5usec, i.e. trigger in the centre
    i.set_timebase(-0.01, 0.01)
    sample_rate = i.get_samplerate()
    print(f"Sample rate: {sample_rate}")

    # Generate an output sine wave on Channel 1, 1Vpp, 1MHz, 0V offset
    #i.generate_waveform(1, 'Sine', amplitude=1, frequency=1e6)

    # Set the data source of Channel 1 to be Input 1
    i.set_source(1, 'Input1')

    # Set the data source of Channel 2 to the generated output sinewave
    i.set_source(2, 'Input2')


    # Get initial data frame to set up plotting parameters. This can be done
    # once if we know that the axes aren't going to change (otherwise we'd do
    # this in the loop)
    data = i.get_data()

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
    time_separation = 60 * 3 # seconds
    n = 0
    start_time = time.time()
    print("Start time:", start_time)
    while True:
        # Get new data
        data = i.get_data()
        abs_time = time.time() 
        current_time = abs_time - start_time
        if current_time>=n*time_separation:
            savedata(data, [abs_time, current_time, sample_rate], file_prefix=f"data_{n}")
            n+=1

        # Update the plot
        line1.set_ydata(np.array(data['ch1'])+0.2)
        line2.set_ydata(np.array(data['ch2'])/20)
        line1.set_xdata(data['time'])
        line2.set_xdata(data['time'])
        plt.pause(0.001)
        
except Exception as e:
    i.relinquish_ownership()
    raise e
finally:
    # Close the connection to the Moku device
    # This ensures network resources and released correctly
    i.relinquish_ownership()
