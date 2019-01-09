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

READ_ALL_AVAILABLE = -1

channels = [0]
channel_mask = chan_list_to_mask(channels)
num_channels = len(channels)

samples_per_channel = 0

options = OptionFlags.CONTINUOUS

scan_rate = 1000

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
    print('         mcc118.a_in_scan_stop')
    print('    Channels: ', end='')
    print(', '.join([str(chan) for chan in channels]))
    print('    Requested scan rate: ', scan_rate)
    print('    Actual scan rate: ', actual_scan_rate)
    print('    Options: ', enum_mask_to_string(OptionFlags, options))

    # try:
    # input('\nPress ENTER to continue ...')
    # except (NameError, SyntaxError):
    # pass

    # Configure and start the scan.
    # Since the continuous option is being used, the samples_per_channel
    # parameter is ignored if the value is less than the default internal
    # buffer size (10000 * num_channels in this case). If a larger internal
    # buffer size is desired, set the value of this parameter accordingly.
    hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate,
                        options)

    print('Starting scan ... Press Ctrl-C to stop\n')

    total_samples_read = 0
    read_request_size = READ_ALL_AVAILABLE
    timeout = 5.0

    while True:
        read_result = hat.a_in_scan_read(read_request_size, timeout)

        samples_read_per_channel = int(len(read_result.data) / num_channels)
        total_samples_read += samples_read_per_channel
        index = total_samples_read
        np.savetxt('softtrigger.txt', index)



    # When doing a continuous scan, the timeout value will be ignored in the
    # call to a_in_scan_read because we will be requesting that all available
    # samples (up to the default buffer size) be returned.




except (HatError, ValueError) as err:
    print('\n', err)