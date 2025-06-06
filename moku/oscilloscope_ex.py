#
# moku example: Basic Oscilloscope
#
# This script demonstrates how to use the Oscilloscope instrument
# to retrieve a single frame of dual-channel voltage data.
#
# (c) Liquid Instruments Pty. Ltd.
#
from moku.instruments import Oscilloscope

# Connect to your Moku by its ip address using Oscilloscope('192.168.###.###')
# force_connect will overtake an existing connection
i = Oscilloscope('192.168.73.1', force_connect=True)

try:
    # Set the span to from -1ms to 1ms i.e. trigger point centred
    i.set_timebase(-1e-4, 1e-4)

    # Get and print a single frame  of data (time series
    # of voltage per channel)
    data = i.get_data()
    print(i.get_samplerate())


except Exception as e:
    i.relinquish_ownership()
    raise e
finally:
    # Close the connection to the Moku device
    # This ensures network resources are released correctly
    i.relinquish_ownership()
