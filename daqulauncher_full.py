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
from daqhats import mcc118, OptionFlags, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, \
chan_list_to_mask
import math as mt   # Added the math package
import pyodbc
import sys

"""FRAMES"""
root = Tk()
root.title("DAQ Launcher")

f1 = Frame(root, width=400, height=80)
f1.pack(side=TOP)

f2 = Frame(root, width=400, height=100)
f2.pack(side=BOTTOM)

""""VARIABLES"""
idvar = 1
chanvar = StringVar()
ratevar = StringVar()
totvar = StringVar()
id = idvar.get()
chan = chanvar.get()
rate = ratevar.get()
tot = totvar.get()
print(id, chan, rate, tot)
"""FUNCTIONS TO CALL"""
def fs(id, chan, rate, tot):
    print(idvar.get(), chanvar.get(), ratevar.get(), totvar.get())
    """
        This function is executed automatically when the module is run directly.
        """

    # Store the channels in a list and convert the list to a channel mask that
    # can be passed as a parameter to the MCC 118 functions.
    no_of_channels = chan  # Creates the list of channels.
    channels = np.ndarray.tolist(np.arange((no_of_channels), dtype=int))
    channel_mask = chan_list_to_mask(channels)
    num_channels = len(channels)

    samples_per_channel = tot
    if (num_channels % 2) == 0:
        samples = int(samples_per_channel * num_channels)
    else:
        samples = int(mt.ceil(samples_per_channel * num_channels))

    scan_rate = rate
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

        # try:
        # input('\nPress ENTER to continue ...')
        # except (NameError, SyntaxError):
        # pass

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
        ID = id
        Force = max(read_output.data) * 12
        Temp = temperature()

        print(Force)
        print(Temp)
        database_upload(now, ID, Force, Temp)
        # Display the header row for the data table.
        # print('Samples Read    Scan Count', end='')
        # for chan in channels:
        # print('    Channel ', chan, sep='', end='')
        # print('')

        # try:
        # read_and_display_data(hat, samples_per_channel, num_channels)

        # except KeyboardInterrupt:
        # Clear the '^C' from the display.
        # print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')

    except (HatError, ValueError) as err:
        print('\n', err)


def cs():
    subprocess.call('python ./mcc/continuous_scan.py')

def fswt():
    os.system('python ./mcc/finite_scan_with_trigger.py')

"""LAUNCHER BUTTONS"""
finitebutton = Button(f1, text="Finite Scan", command=fs)
finitebutton.grid(row=0, column=0, pady=10)

continuousbutton = Button(f1, text="Continuous Scan", command=cs)
continuousbutton.grid(row=0, column=1, pady=10)

fcwtbutton = Button(f1, text="Finite Scan w/Trigger", command=fswt)
fcwtbutton.grid(row=0, column=2, pady=10)

"""INPUTS"""
idin = Label(f2, text=idvar, justify='center')
idin.grid(row=0, column=1, padx=20, pady=10)
chanin = Entry(f2, textvariable=chanvar, justify='center')
chanin.grid(row=1, column=1, padx=20, pady=10)
ratein = Entry(f2, textvariable=ratevar, justify='center')
ratein.grid(row=2, column=1, padx=20, pady=10)
totin = Entry(f2, textvariable=totvar, justify='center')
totin.grid(row=3, column=1, padx=20, pady=10)

"""LABELS"""

idlab = Label(f2, text="DataBox ID")
idlab.grid(row=0, column=0)
chanlab = Label(f2, text="Number of channels")
chanlab.grid(row=1, column=0)
ratelab = Label(f2, text="Sample rate (Hz)")
ratelab.grid(row=2, column=0)
totlab = Label(f2, text="Samples per channel")
totlab.grid(row=3, column=0)


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


def load_cell_conv(f):
    return f * 12


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

root.mainloop()