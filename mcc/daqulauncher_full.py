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
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sys
"""PLT FIGSIZE SETUP"""
plt.rcParams["figure.figsize"] = (4.2,2.4)

"""ALL FUNCTIONS"""
def fs():
    # Update Status
    status.config(text="Running...")
    status.update()
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

        try:
            print('Starting scan ... Press Ctrl-C to stop\n')
            status.config(text="Scanning...")
            status.update()

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
            Force = float("{0:.2f}".format(max(read_output.data) * 12))
            Temp = temperature()

            hat.a_in_scan_stop()
            hat.a_in_scan_cleanup()

            print(Force)
            print(Temp)
            database_upload(now, ID, Force, Temp)

            Plot(force_data)
            ResultsWindow(Force, Temp)

            # Update Status
            status.config(text="Finished...")
            status.update()

        except KeyboardInterrupt:
            # Clear the '^C' from the display.
            print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')

    except (HatError, ValueError) as err:
        print('\n', err)

def cs():
    subprocess.call('python ./mcc/continuous_scan.py')

def fswt():
    # Update Status
    status.config(text="Running...")
    status.update()
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
    trigger_mode = TriggerModes.RISING_EDGE
    timeout = 5.0

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
            status.config(text="Waiting...")
            status.update()
            wait_for_trigger(hat)

            print('\nStarting scan ... Press Ctrl-C to stop\n')
            status.config(text="Triggered")
            status.update()

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
            Force = float("{0:.2f}".format(max(read_output.data) * 12))
            Temp = temperature()

            print(Force)
            print(Temp)
            database_upload(now, ID, Force, Temp)

            hat.a_in_scan_stop()
            hat.a_in_scan_cleanup()

            Plot(force_data)
            ResultsWindow(Force, Temp)

            status.config(text="Finished...")
            status.update()

        except KeyboardInterrupt:
            # Clear the '^C' from the display.
            print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')

    except (HatError, ValueError) as err:
        print('\n', err)

def fswtl():
    # Update Status
    status.config(text="Running...")
    status.update()

    i = 1
    while i < 6:
        """This function is executed automatically when the module is run directly.
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
        trigger_mode = TriggerModes.RISING_EDGE
        timeout = 5.0

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
                status.config(text="Waiting...")
                status.update()
                wait_for_trigger(hat)

                print('\nStarting scan ... Press Ctrl-C to stop\n')
                status.config(text="Triggered")
                status.update()

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
                Force = float("{0:.2f}".format(max(read_output.data) * 12))
                Temp = temperature()

                print(Force)
                print(Temp)
                database_upload(now, ID, Force, Temp)

                hat.a_in_scan_stop()
                hat.a_in_scan_cleanup()

                # Counter stepping
                counter.set(counter.get() + 1)
                f = open('count.txt', 'w')
                f.write(str(counter.get()))
                f.close()

                Plot(force_data)
                ResultsWindow(Force, Temp)

            except KeyboardInterrupt:
                # Clear the '^C' from the display.
                print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')

        except (HatError, ValueError) as err:
            print('\n', err)

def Quit():
    root.destroy()

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

def temperature():
    # Raspberry Pi software SPI configuration.
    CLK = 25
    CS = 24
    DO = 18
    sensor = MAX31855.MAX31855(CLK, CS, DO)
    temp = sensor.readTempC()
    if np.isnan(temp) == True:
        temp = None
    else:
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
    #Clear all widgets from f3
    for widget in f3.winfo_children():
        widget.destroy()

    #clear plot
    plt.clf()

    #draw plot
    fig = plt.figure(1, figsize=[3.2,2.4])
    plt.ion()
    plt.plot(force_data)

    canvas = FigureCanvasTkAgg(fig, master=f3)
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

def database_upload(now, ID, Force, Temp):
    con = pyodbc.connect("DSN=RIVWARE;UID=dataguys;PWD=dataguys;TDS_Version=4.2")
    cursor = con.cursor()
    print('Uploading...')

    cursor.execute("INSERT INTO dbo.Data2 ([Date Time], ID, Force, Temperature) VALUES (?, ?, ?, ?)", now, ID, Force,
                   Temp)
    con.commit()

    con.close()
    print('Data Upload Successful')

def ResultsWindow(Force, Temp):

    ResultForce.config(text=Force)
    ResultForce.update()
    ResultTemp.config(text=Temp)
    ResultTemp.update()

""""All code Running here"""
"""FRAMES"""
root = Tk()
root.title("DAQ Launcher")
root.minsize(800,400)

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=5)

control = Frame(root, borderwidth=2, relief=RAISED)
control.grid_columnconfigure(0, weight=1)
control.grid(row=0, column=0, sticky=N+S+E+W)

inout = Frame(root)
inout.grid(row=1, column=0, sticky=N+S+E+W)

inout.grid_columnconfigure(0, weight=1)
inout.grid_columnconfigure(1, weight=3)
inout.grid_rowconfigure(0, weight=1)

f1 = Frame(control)
f1.grid(row=0, column=0)

f2 = Frame(inout, borderwidth=2, relief=RAISED)
f2.grid(row=0, column=0, sticky=W+E+N+S)
f2.grid_columnconfigure(0, weight=1)
f2.grid_columnconfigure(3, weight=1)
f2.grid_rowconfigure(0, weight=1)
f2.grid_rowconfigure(8, weight=1)

f3 = Frame(inout, relief=RAISED)
f3.grid(row=0, column=1, sticky=W+E+N+S)

""""VARIABLES"""
idvar = StringVar()
chanvar = StringVar()
ratevar = StringVar()
totvar = StringVar()
trigvar = StringVar()
counter = IntVar()
idvar.set(1)
chanvar.set(1)
ratevar.set(4000)
totvar.set(1000)
trigvar.set("TriggerModes.RISING_EDGE")
f = open("count.txt", "r")
counter.set(f.read())

"""INPUTS"""
idin = OptionMenu(f2, idvar, 1, 2, 3, 4, 5, 6, 7, 8)
idin.grid(row=1, column=2, padx=20, pady=10)
chanin = OptionMenu(f2, chanvar, 1, 2, 3, 4, 5, 6, 7, 8)
chanin.grid(row=2, column=2, padx=20, pady=10)
ratein = OptionMenu(f2, ratevar, 500, 1000, 2000, 4000, 8000)
ratein.grid(row=3, column=2, padx=20, pady=10)
totin = OptionMenu(f2, totvar, 500, 1000, 2000, 5000, 10000)
totin.grid(row=4, column=2, padx=20, pady=10)
trigin1 = Radiobutton(f1, text="Trigger Rising", variable=trigvar, value="TriggerModes.RISING_EDGE")
trigin2 = Radiobutton(f1, text="Trigger Falling", variable=trigvar, value="TriggerModes.FALLING_EDGE")
trigin1.grid(row=1, column=2)
trigin2.grid(row=2, column=2)
counterin = Entry(f1, textvariable=counter)
counterin.grid(row=2, column=3)

"""LABELS"""
idlab = Label(f2, text="DataBox ID")
idlab.grid(row=1, column=1)
chanlab = Label(f2, text="Number of channels")
chanlab.grid(row=2, column=1)
ratelab = Label(f2, text="Sample rate (Hz)")
ratelab.grid(row=3, column=1)
totlab = Label(f2, text="Sample duration (ms)")
totlab.grid(row=4, column=1)
counterlab = Label(f1, text="Starting Cycle Count")
counterlab.grid(row=1, column=3)
statuslab = Label(f1, text="Scanner Status:")
statuslab.grid(row=1, column=0, columnspan=2)
status = Label(f1, text="Ready...", fg='red', bg='white', relief=SUNKEN, width=10)
status.grid(row=2, column=0, columnspan=2)
LabelForce = Label(f2, text="Force (kN)")
LabelForce.grid(row=5, column=1)
LabelTemp = Label(f2, text="Temp (C)")
LabelTemp.grid(row=6, column=1)
ResultForce = Label(f2, text="Force", fg='red', bg='white', relief=SUNKEN, width=10)
ResultForce.grid(row=5, column=2)
ResultTemp = Label(f2, text="Temp", fg='red', bg='white', relief=SUNKEN, width=10)
ResultTemp.grid(row=6, column=2)

"""LAUNCHER BUTTONS"""
finitebutton = Button(f1, text="Finite Scan", command=fs)
finitebutton.grid(row=0, column=0, pady=10)

continuousbutton = Button(f1, text="Continuous Scan", command=cs)
continuousbutton.grid(row=0, column=1, pady=10)

fcwtbutton = Button(f1, text="Finite Scan w/Trigger", command=fswt)
fcwtbutton.grid(row=0, column=2, pady=10)

fcwtlbutton = Button(f1, text="Looped Triggered Scan", command=fswtl)
fcwtlbutton.grid(row=0, column=3, pady=10)

root.mainloop()
