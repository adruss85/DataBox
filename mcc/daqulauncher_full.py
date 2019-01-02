#!/usr/bin/python

from __future__ import print_function
import os
import subprocess
from Tkinter import*
import numpy as np
import datetime
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
from time import sleep
from sys import stdout
from daqhats import mcc118, OptionFlags, TriggerModes, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, \
chan_list_to_mask
import math as mt   # Added the math package
import pyodbc
import matplotlib.pyplot as plt
import sys

"""FRAMES"""
root = Tk()
root.title("DAQ Launcher")

f1 = Frame(root, width=400, height=80)
f1.pack(side=TOP)

f2 = Frame(root, width=400, height=100)
f2.pack(side=BOTTOM)

""""VARIABLES"""
idvar = StringVar()
chanvar = StringVar()
ratevar = StringVar()
totvar = StringVar()
trigvar = StringVar()
idvar.set(1)
chanvar.set(1)
ratevar.set(4000)
totvar.set(1000)
trigvar.set("TriggerModes.RISING_EDGE")

"""FUNCTIONS TO CALL"""
def fs():
    """
        This function is executed automatically when the module is run directly.
        """

    # Store the channels in a list and convert the list to a channel mask that
    # can be passed as a parameter to the MCC 118 functions.
    no_of_channels = int(chanvar.get())  # Creates the list of channels.
    channels = np.ndarray.tolist(np.arange((no_of_channels), dtype=int))
    channel_mask = chan_list_to_mask(channels)
    num_channels = len(channels)
    
    samples_per_channel = int(totvar.get())/1000*int(ratevar.get())
    if (num_channels % 2) == 0:
        samples = int(samples_per_channel * num_channels)
    else:
        samples = int(mt.ceil(samples_per_channel * num_channels))

    scan_rate = int(ratevar.get())
    options = OptionFlags.DEFAULT
    timeout = 10.0

    try:
        # Select an MCC 118 HAT device to use.
        address = select_hat_device(HatIDs.MCC_118)
        hat = mcc118(address)

        print('\nSelected MCC 118 HAT device at address', address)

        actual_scan_rate = hat.a_in_scan_actual_rate(num_channels, scan_rate)

        print('\nMCC 118 continuous scan example')
        print('    Functions demonstrated:')
        print('         mcc118.a_in_scan_start')
        print('         mcc118.a_in_scan_read')
        print('    Channels: ', end='')
        print(', '.join([str(chan) for chan in channels]))
        print('    Requested scan rate: ', scan_rate)
        print('    Actual scan rate: ', actual_scan_rate)
        print('    Samples per channel', samples_per_channel)
        print('    Options: ', enum_mask_to_string(OptionFlags, options))

        # Configure and start the scan.
        hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate,
                            options)

        print('Starting scan ... Press Ctrl-C to stop\n')

        """read complete output data and place int array"""
        read_output = hat.a_in_scan_read_numpy(samples_per_channel, timeout)
        """create a blank array"""
        chan_data = np.zeros([samples_per_channel, num_channels])
        """create title array"""
        chan_title = []
        force_data = read_output.data * 12
        """iterate through the array per channel to split out every other
        sample into the correct column"""

        for i in range(num_channels):
            for j in range(samples_per_channel):
                if j == 0:
                    y = str('Channel') + ' ' + str(i)
                    chan_title.append(str(y))
            if i < samples_per_channel - num_channels:
                chan_data[:, i] = force_data[i::num_channels]

        print('Iterated through loop\n')

        chan_final = np.concatenate((np.reshape(np.array(chan_title), (1, num_channels)), chan_data), axis=0)
        np.savetxt('foo.csv', chan_final, fmt='%5s', delimiter=',')

        now = datetime.datetime.now()
        ID = int(idvar.get())
        Force = max(read_output.data) * 12
        Temp = temperature()

        print(Force)
        print(Temp)
        database_upload(now, ID, Force, Temp)

        Plot(force_data)
        ResultsWindow(Force, Temp)

    except (HatError, ValueError) as err:
        print('\n', err)


def cs():
    subprocess.call('python ./mcc/continuous_scan.py')

def fswt():
    """
           This function is executed automatically when the module is run directly.
           """

    # Store the channels in a list and convert the list to a channel mask that
    # can be passed as a parameter to the MCC 118 functions.
    no_of_channels = int(chanvar.get())  # Creates the list of channels.
    channels = np.ndarray.tolist(np.arange((no_of_channels), dtype=int))
    channel_mask = chan_list_to_mask(channels)
    num_channels = len(channels)

    samples_per_channel = int(totvar.get()) / 1000 * int(ratevar.get())
    if (num_channels % 2) == 0:
        samples = int(samples_per_channel * num_channels)
    else:
        samples = int(mt.ceil(samples_per_channel * num_channels))

    scan_rate = int(ratevar.get())
    options = OptionFlags.EXTTRIGGER
    trigger_mode = trigvar.get()


    try:
        # Select an MCC 118 HAT device to use.
        address = select_hat_device(HatIDs.MCC_118)
        hat = mcc118(address)

        print('\nSelected MCC 118 HAT device at address', address)

        actual_scan_rate = hat.a_in_scan_actual_rate(num_channels, scan_rate)

        print('\nMCC 118 continuous scan example')
        print('    Functions demonstrated:')
        print('         mcc118.trigger_mode')
        print('         mcc118.a_in_scan_status')
        print('         mcc118.a_in_scan_start')
        print('         mcc118.a_in_scan_read')
        print('    Channels: ', end='')
        print(', '.join([str(chan) for chan in channels]))
        print('    Requested scan rate: ', scan_rate)
        print('    Actual scan rate: ', actual_scan_rate)
        print('    Samples per channel', samples_per_channel)
        print('    Options: ', enum_mask_to_string(OptionFlags, options))
        print('    Trigger Mode: ', trigger_mode.name)

        hat.trigger_mode(trigger_mode)

        # Configure and start the scan.
        hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate,
                            options)

        try:
            # wait for the external trigger to occur
            print('\nWaiting for trigger ... hit Ctrl-C to cancel the trigger')
            wait_for_trigger(hat)

            print('\nStarting scan ... Press Ctrl-C to stop\n')

            """read complete output data and place int array"""
            read_output = hat.a_in_scan_read_numpy(samples_per_channel, timeout)
            """create a blank array"""
            chan_data = np.zeros([samples_per_channel, num_channels])
            """create title array"""
            chan_title = []
            force_data = read_output.data * 12
            """iterate through the array per channel to split out every other
            sample into the correct column"""

            for i in range(num_channels):
                for j in range(samples_per_channel):
                    if j == 0:
                        y = str('Channel') + ' ' + str(i)
                        chan_title.append(str(y))
                if i < samples_per_channel - num_channels:
                    chan_data[:, i] = force_data[i::num_channels]

            print('Iterated through loop\n')

            chan_final = np.concatenate((np.reshape(np.array(chan_title), (1, num_channels)), chan_data), axis=0)
            np.savetxt('foo.csv', chan_final, fmt='%5s', delimiter=',')

            now = datetime.datetime.now()
            ID = int(idvar.get())
            Force = max(read_output.data) * 12
            Temp = temperature()

            print(Force)
            print(Temp)
            database_upload(now, ID, Force, Temp)

            Plot(force_data)
            ResultsWindow(Force, Temp)

        except KeyboardInterrupt:
            # Clear the '^C' from the display.
            print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')

    except (HatError, ValueError) as err:
        print('\n', err)


"""LAUNCHER BUTTONS"""
finitebutton = Button(f1, text="Finite Scan", command=fs)
finitebutton.grid(row=0, column=0, pady=10)

continuousbutton = Button(f1, text="Continuous Scan", command=cs)
continuousbutton.grid(row=0, column=1, pady=10)

fcwtbutton = Button(f1, text="Finite Scan w/Trigger", command=fswt)
fcwtbutton.grid(row=0, column=2, pady=10)

"""INPUTS"""
idin = OptionMenu(f2, idvar, 1, 2, 3, 4, 5, 6, 7, 8)
idin.grid(row=0, column=1, padx=20, pady=10)
chanin = OptionMenu(f2, chanvar, 1, 2, 3, 4, 5, 6, 7, 8)
chanin.grid(row=1, column=1, padx=20, pady=10)
ratein = OptionMenu(f2, ratevar, 500, 1000, 2000, 4000, 8000)
ratein.grid(row=2, column=1, padx=20, pady=10)
totin = OptionMenu(f2, totvar, 500, 1000, 2000, 5000, 10000)
totin.grid(row=3, column=1, padx=20, pady=10)
trigin1 = Radiobutton(f1, text="Trigger Rising", variable=trigvar, value="TriggerModes.RISING_EDGE")
trigin2 = Radiobutton(f1, text="Trigger Falling", variable=trigvar, value="TriggerModes.FALLING_EDGE")
trigin1.grid(row=1, column=2)
trigin2.grid(row=2, column=2)

"""LABELS"""

idlab = Label(f2, text="DataBox ID")
idlab.grid(row=0, column=0)
chanlab = Label(f2, text="Number of channels")
chanlab.grid(row=1, column=0)
ratelab = Label(f2, text="Sample rate (Hz)")
ratelab.grid(row=2, column=0)
totlab = Label(f2, text="Sample duration (ms)")
totlab.grid(row=3, column=0)

"""ALL SUBFUNCTIONS"""
def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0


def temperature():
    # Raspberry Pi software SPI configuration.
    CLK = 25
    CS = 24
    DO = 18
    sensor = MAX31855.MAX31855(CLK, CS, DO)
    temp = sensor.readTempC()
    internal = sensor.readInternalC()
    # print('Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp)))
    return temp

def wait_for_trigger(hat):
    """
    Monitor the status of the specified HAT device in a loop until the
    triggered status is True or the running status is False.

    Args:
        hat (mcc118): The mcc118 HAT device object on which the status will
            be monitored.

    Returns:
        None

    """
    # Read the status only to determine when the trigger occurs.
    is_running = True
    is_triggered = False
    while is_running and not is_triggered:
        status = hat.a_in_scan_status()
        is_running = status.running
        is_triggered = status.triggered

def load_cell_conv(f):
    return f * 12

def Plot(force_data):
    plt.plot(force_data)
    plt.ylabel('some numbers')
    plt.show()

def database_upload(now, ID, Force, Temp):
    con = pyodbc.connect("DSN=RIVWARE;UID=dataguys;PWD=dataguys;TDS_Version=4.2")
    cursor = con.cursor()
    # print(con)
    print('Uploading...')

    cursor.execute("INSERT INTO dbo.Data2 ([Date Time], ID, Force, Temperature) VALUES (?, ?, ?, ?)", now, ID, Force,
                   Temp)
    con.commit()

    con.close()
    print('Data Upload Successful')

def ResultsWindow(Force, Temp):
    root2 = Tk()
    root2.title("Results")

    LabelForce = Label(root2, text="Force (kN)")
    LabelForce.grid(row=0, column=0)
    LabelTemp = Label(root2, text="Temp (C)")
    LabelTemp.grid(row=1, column=0)
    ResultForce = Label(root2, text=Force)
    ResultForce.grid(row=0, column=1)
    ResultTemp = Label(root2, text=Temp)
    ResultTemp.grid(row=1, column=1)

    root2.mainloop()

root.mainloop()
