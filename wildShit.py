# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 17:32:01 2019

@author: apasi
"""

import Adafruit_BBIO.PWM as PWM
import time as t
import Adafruit_BBIO.GPIO as GPIO
 
PWM.start("P8_13",25,1000)
 
#t.sleep(5)
 
PWM.stop("P8_13")
 
PWM.cleanup()
 
GPIO.setup("P8_15", GPIO.OUT)
GPIO.setup("P8_16", GPIO.IN)
 
GPIO.output("P8_15", 1)
while(1):
    print(GPIO.input("P8_16"))