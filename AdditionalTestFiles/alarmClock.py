import signal
import subprocess
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time
import datetime
import os
import sqlite3

db = sqlite3.connect('baza.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS alarmy(id INT PRIMARY KEY,user TEXT, godzina INT, minuty INT);')

# Setup
ampm = 0  # AM/PM Flag
alarm = 0  # Alarm Flag
alarm_hour = 0
alarm_minute = 0
proc = None  # Setup Proc for sound playing

button1 = "P8_08"  # InitializeButtons
button2 = "P8_10"
button3 = "P8_12"
button4 = "P8_16"

led1 = "P8_07"
led2 = "P8_09"
led3 = "P8_11"
led4 = "P8_15"


LEDalarmOnOff = "P9_26"  # Initialize LEDs
LEDampm = "P9_27"

GPIO.setup(button1, GPIO.IN)  # Set correct functions for buttons and LEDs
GPIO.setup(button2, GPIO.IN)
GPIO.setup(button3, GPIO.IN)
GPIO.setup(button4, GPIO.IN)
GPIO.setup(led1, GPIO.OUT)  # Set correct functions for buttons and LEDs
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(led3, GPIO.OUT)
GPIO.setup(led4, GPIO.OUT)
GPIO.setup(LEDalarmOnOff, GPIO.OUT)
GPIO.setup(LEDampm, GPIO.OUT)

GPIO.output(LEDalarmOnOff, alarm)


def update():  # Main method to update Seven Segment Display
    global ampm
    global alarm
    global alarm_hour
    global alarm_minute
    while (1):
        # Continually check for correct time
        datetime_hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        hour = datetime_hour
        alarm_hour_ampm = alarm_hour

        # Correction for 24 our time
        if datetime_hour > 12:
            hour = datetime_hour - 12
        if alarm_hour > 12:
            alarm_hour_ampm = alarm_hour - 12

        # Turning Alarm on at correct time
        if alarm == 1 and alarm_hour == datetime_hour and alarm_minute == minute:
            alarm_on()
            alarm = 0
            GPIO.output(LEDalarmOnOff, alarm)

        # Showing Alarm or setting time
        if GPIO.input("P9_22"):
            #set_7seg(alarm_hour_ampm, alarm_minute)
            if alarm_hour < 12:
                ampm = 0
            else:
                ampm = 1
        else:
            #set_7seg(hour, minute)
            if datetime_hour < 12:
                ampm = 0
            else:
                ampm = 1
        GPIO.output(LEDampm, ampm)  # Setting AM/PM LED


def alarm_on():
    global proc
    # Running cvlc from console for youtube.  Enter desired youtube link here.
    PWM.start("P8_13", 25, 1000)
    
    return 0


def alarm_off(channel):
    # Killing cvlc to turn off alarm
    global proc
    #proc.send_signal(signal.SIGINT)
    for i in range(5):
    rand=random.randrange(1,5,1)
    button = 0
    if random==1:
        GPIO.output("P8_7", GPIO.HIGH)
        while button==0:
            button=GPIO.input("P8_8")
        while button==1:
            button=GPIO.input("P8_8")
        GPIO.output("P8_7", GPIO.LOW)
    elif random==2:
        GPIO.output("P8_9", GPIO.HIGH)
        while button==0:
            button=GPIO.input("P8_10")
        while button==1:
            button=GPIO.input("P8_10")
        GPIO.output("P8_9", GPIO.LOW)
    elif random == 3:
        GPIO.output("P8_11", GPIO.HIGH)
        while button==0:
            button=GPIO.input("P8_12")
        while button==1:
            button=GPIO.input("P8_12")
        GPIO.output("P8_11", GPIO.LOW)
    elif random==4:
        GPIO.output("P8_15", GPIO.HIGH)
        while button==0:
            button=GPIO.input("P8_16")
        while button==1:
            button=GPIO.input("P8_16")
        GPIO.output("P8_15", GPIO.LOW)
    PWM.stop("P8_13")
    PWM.cleanup()
    
    return 0

def add_alarm(int godzina, int minuta):
    cursor.execute('SELECT MAX(id) FROM alarmy;')
    id_val = cursor.fetchall()
    id_val = id_val + 1
    global user
    cursor.execute('INSERT INTO alarmy VALUES(?,?,?,?);',(id_val,user, godzina, minuta))

def set_alarm(int id_val):
    cursor.execute("SELECT godzina, minuty FROM alarmy WHERE id=?;", (id_val))
    values = cursor.fetchall()
    #set alarm with values here
    #TODO

# Turn Alarm on or off
def alarm_toggle(channel):
    global alarm
    if alarm == 1:
        alarm = 0
    else:
        alarm = 1
    GPIO.output(LEDalarmOnOff, alarm)


# Setting Alarm Hour
def set_alarm_hour(channel):
    global alarm_hour
    if alarm_hour == 23:
        alarm_hour = 0
    else:
        alarm_hour = alarm_hour + 1


# Setting Alarm minute
def set_alarm_minute(channel):
    global alarm_minute
    if alarm_minute == 59:
        alarm_minute = 0
    else:
        alarm_minute = alarm_minute + 1


# Write to Seven Segment
"""def set_7seg(hour, minute):
    segment.clear()
    # Set hours
    segment.set_digit(0, int(hour / 10))
    segment.set_digit(1, hour % 10)
    # Set minutes
    segment.set_digit(2, int(minute / 10))
    segment.set_digit(3, minute % 10)
    # Toggle colon
    segment.set_colon(datetime.datetime.now().second % 2)

    # Update the actual display LEDs.
    segment.write_display()

    # Wait a quarter second
    time.sleep(0.25)
    return 0"""


# GPIO Events for button presses
GPIO.add_event_detect(button1, GPIO.FALLING, callback=alarm_off, bouncetime=200)
GPIO.add_event_detect(button2, GPIO.FALLING, callback=set_alarm_hour, bouncetime=200)
GPIO.add_event_detect(button3, GPIO.FALLING, callback=set_alarm_minute, bouncetime=200)
GPIO.add_event_detect(button4, GPIO.FALLING, callback=alarm_toggle, bouncetime=200)

# Call the main function
update()