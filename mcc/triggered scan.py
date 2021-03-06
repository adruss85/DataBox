#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
    MCC 118 Functions Demonstrated:
        mcc118.trigger_mode
        mcc118.a_in_status
        mcc118.a_in_scan_start
        mcc118.a_in_scan_read

    Purpose:
        Perform a triggered finite acquisition on 1 or more channels.

    Description:
        Waits for an external trigger to occur and then acquires blocks
        of analog input data for a user-specified group of channels.  The
        last sample of data for each channel is displayed for each block
        of data received from the device.  The acquisition is stopped when
        the specified number of samples is acquired for each channel.
"""

from __future__ import print_function
import numpy as np
import datetime
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
from time import sleep
from sys import stdout
from daqhats import mcc118, OptionFlags, TriggerModes, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, \
    chan_list_to_mask


CURSOR_BACK_2 = '\x1b[2D'
ERASE_TO_END_OF_LINE = '\x1b[0K'

def main():
    """
    This function is executed automatically when the module is run directly.
    """
    # Store the channels in a list and convert the list to a channel mask that
    # can be passed as a parameter to the MCC 118 functions.
    channels = [0,1]
    channel_mask = chan_list_to_mask(channels)
    num_channels = len(channels)

    samples_per_channel = 4000
    scan_rate = 4000
    options = OptionFlags.EXTTRIGGER
    trigger_mode = TriggerModes.ACTIVE_HIGH
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

        #try:
            #input('\nPress ENTER to continue ...')
        #except (NameError, SyntaxError):
            #pass

        hat.trigger_mode(trigger_mode)

        # Configure and start the scan.
        hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate,
                            options)

        #try:
        # wait for the external trigger to occur
        print('\nWaiting for trigger ... hit Ctrl-C to cancel the trigger')
        wait_for_trigger(hat)

        print('\nStarting scan ... Press Ctrl-C to stop\n')

        """read complete output data and place int array"""
    	read_output = hat.a_in_scan_read_numpy(samples_per_channel, timeout)
    	"""create a blank array"""
    	chan_data = np.zeros([samples_per_channel, num_channels])
    	chan_title = []
        for i in range(num_channels):
            for j in range(samples_per_channel):
                if j ==0:
                    y = str('Channel') + ' ' + str(i)
                    chan_title.append(str(y))
            chan_data[:, i] = read_output.data[i]
        chan_final = np.concatenate((np.reshape(np.array(chan_title), (1, num_channels)), chan_data), axis = 0)
    
    	np.savetxt('force_data.csv', chan_final, fmt = '%5s', delimiter = ',')
    
    	for i in range (num_channels):
        	max_data = max(chan_data[:,i])
        	print("Max Ch",(i),":", max_data)

    	temperature()
    	print(temperature())
        print(max(read_output.data)*12)

        #except KeyboardInterrupt:
            # Clear the '^C' from the display.
            #print(CURSOR_BACK_2, ERASE_TO_END_OF_LINE, '\n')

    except (HatError, ValueError) as err:
        print('\n', err)


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


def read_and_display_data(hat, samples_per_channel, num_channels):
    """
    Reads data from the specified channels on the specified DAQ HAT devices
    and updates the data on the terminal display.  The reads are executed in a
    loop that continues until either the scan completes or an overrun error
    is detected.

    Args:
        hat (mcc118): The mcc118 HAT device object.
        samples_per_channel: The number of samples to read for each channel.
        num_channels (int): The number of channels to display.

    Returns:
        None

    """
    total_samples_read = 0
    read_request_size = 500
    timeout = 5.0

    # Continuously update the display value until Ctrl-C is pressed
    # or the number of samples requested has been read.
    while total_samples_read < samples_per_channel:
        read_result = hat.a_in_scan_read(read_request_size, timeout)

        # Check for an overrun error
        if read_result.hardware_overrun:
            print('\n\nHardware overrun\n')
            break
        elif read_result.buffer_overrun:
            print('\n\nBuffer overrun\n')
            break

        samples_read_per_channel = int(len(read_result.data) / num_channels)
        total_samples_read += samples_read_per_channel

        # Display the last sample for each channel.
        print('\r{:12}'.format(samples_read_per_channel),
              ' {:12} '.format(total_samples_read), end='')

        if samples_read_per_channel > 0:
            index = samples_read_per_channel * num_channels - num_channels

            for i in range(num_channels):
                print('{:10.5f}'.format(read_result.data[index + i]), 'V ',
                      end='')
            stdout.flush()

            sleep(0.1)

    print('\n')

def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

def temperature():
	# Raspberry Pi software SPI configuration.
    CLK = 25
    CS  = 24
    DO  = 18
    sensor = MAX31855.MAX31855(CLK, CS, DO)
    temp = sensor.readTempC()
    internal = sensor.readInternalC()
    #print('Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp)))
    return temp


if __name__ == '__main__':
    main()
