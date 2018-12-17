#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
    MCC 118 Functions Demonstrated:
        mcc118.a_in_scan_start
        mcc118.a_in_scan_read

    Purpose:
        Perform a finite acquisition on 1 or more channels.

    Description:
        Acquires blocks of analog input data for a user-specified group
        of channels.  The last sample of data for each channel is
        displayed for each block of data received from the device.  The
        acquisition is stopped when the specified number of samples is
        acquired for each channel.

"""
#from __future__ import print_function
#import numpy as np
import datetime
#import Adafruit_GPIO.SPI as SPI
#import Adafruit_MAX31855.MAX31855 as MAX31855
#from time import sleep
#from sys import stdout
#from daqhats import mcc118, OptionFlags, HatIDs, HatError
#from daqhats_utils import select_hat_device, enum_mask_to_string, \
#chan_list_to_mask
import pyodbc


def main():

    now = datetime.datetime.now()
    ID = '1'
    Force = '32.5435345'
    Temp = '24'

    database_upload(now, ID, Force, Temp)


def database_upload(now, ID, Force, Temp):

    con = pyodbc.connect("DSN=RIVWARE;UID=dataguys;PWD=dataguys;TDS_Version=4.2")
    cursor = con.cursor()
    print(con)
    print('Connected')

    cursor.execute("INSERT INTO dbo.Data ([Date Time], ID, Force, Temperature) VALUES (?, ?, ?, ?)", now, ID, Force, Temp) 
    con.commit()

    con.close()

if __name__ == '__main__':
    main()
