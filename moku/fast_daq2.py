# Make sure you're in base conda env this computer's conda configuration is wonky
import time
import numpy as np
from threading import Thread
from moku.instruments import Oscilloscope
import matplotlib.pyplot as plt

# Config
#DEVICE_IP = '192.168.73.1'  # if using Wireless
DEVICE_IP = '[fe80::7269:79ff:feb9:630a%256]' # if using USB-C
DATA_FOLDER = '5-12'
TRACE_DURATION = 0.020         # 20 ms per trace
CYCLE_TIME = 0.020             # 50 ms between captures
NUM_CYCLES = 5                 # How many captures

def save_data(data, timestamp):
    """Save data to compressed numpy file in background"""
    try:
        np.savez_compressed(
            f"{DATA_FOLDER}/capture_{timestamp}.npz",
            time=data['time'],
            ch1=data['ch1'],
            ch2=data['ch2']
        )
    except Exception as e:
        print(f"Save error: {str(e)}")

def plotter(osc, ch1_scale, ch2_scale, ch1_off, ch2_off):
    data = osc.get_data()
    time = np.array(data['time'])
    ch1 = np.array(data['ch1']) * ch1_scale + ch1_off
    ch2 = np.array(data['ch2']) * ch2_scale + ch2_off
    plt.figure()
    plt.plot(time, ch1, label="Channel 1")
    plt.plot(time, ch2, label="Channel 2")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title("Test Trace")
    plt.grid(True)
    plt.legend()
    plt.show()


def main(plot=True, view=[1,0.2,1/20,0]):
    # Connect to device
    osc = Oscilloscope(DEVICE_IP, force_connect=True)
    
    try:
        # Configure oscilloscope
        osc.set_acquisition_mode('Normal')
        osc.set_timebase(-TRACE_DURATION/2, TRACE_DURATION/2)
        osc.set_trigger(type='Edge', source='Input2', level=0)
        osc.set_frontend(channel=1, impedance='1MOhm', coupling="DC", range="10Vpp")
        osc.set_frontend(channel=2, impedance='1MOhm', coupling="DC", range="10Vpp")

        osc.set_source(1, 'Input1')
        osc.set_source(2, 'Input2')

        sample_rate = osc.get_samplerate()
        print(f"Sample rate: {sample_rate}")

        if plot:
            plotter(osc, view[0], view[1], view[2], view[3])

        print("Starting acquisition...")
        n=0
        while n <= NUM_CYCLES:
            cycle_start = time.perf_counter()
            
            # Capture data (blocks until ready)
            capture_start = time.perf_counter()
            data = osc.get_data()
            capture_time = time.perf_counter() - capture_start

            
            # Start async save
            save_start = time.perf_counter()
            Thread(
                target=save_data,
                args=(data.copy(), time.time_ns())  # Pass a copy to avoid race conditions
            ).start()
            save_time = time.perf_counter() - save_start

            # Maintain 50 ms cycle
            elapsed = time.perf_counter() - cycle_start
            sleep_time = CYCLE_TIME - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                print(f"Warning: Cycle {n} lagging by {-sleep_time*1000:.1f}ms")
            print(f"Cycle {n}: Capture Time = {capture_time:.4f}s, Save Time = {save_time:.4f}s, Total Elapsed = {elapsed:.4f}s")
            n+=1

           


    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        osc.relinquish_ownership()

if __name__ == "__main__":
    main()
