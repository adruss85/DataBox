#!/usr/bin/python


import os
import time
import datetime
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
import numpy as np

def temperature():
    CLK = 25
    DO = 18
    CS1 = 24
    CS2 = 23

    sensor1 = MAX31855.MAX31855(CLK, CS1, DO)
    sensor2 = MAX31855.MAX31855(CLK, CS2, DO)

    temp1 = sensor1.readTempC()
    temp2 = sensor2.readTempC()

    return {'Bearing':temp1, 'Motor':temp2}
    
def temperatureloop():
# Raspberry Pi software SPI configuration.
    CLK = 25
    DO = 18
    #Comms pin for TCs
    CS = 4, 17, 27, 22
    lst = []

    for i in CS:
        sensor = MAX31855.MAX31855(CLK, i, DO)
        temp = sensor.readTempC()
        if np.isnan(temp) == True:
            temp = None
        lst.append(temp)

    return lst

temperatureloop()
print lst
 
#temp = temperature()

#print temp['Bearing']
#print temp['Motor']
#print('Thermocouple 2 Temp: {0:0.3F}*C'.format(temperature[temp2]))
  
