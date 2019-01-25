import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import time as t
import random
import sqlite3

# polaczenie z baza
'''db = sqlite3.connect('baza.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS alarmy(id INT PRIMARY KEY,user TEXT, godzina INT, minuty INT);')
db.commit()'''

# inicjalizacja
GPIO.setup("P8_8", GPIO.IN)
GPIO.setup("P8_10", GPIO.IN)
GPIO.setup("P8_12", GPIO.IN)
GPIO.setup("P8_16", GPIO.IN)

GPIO.setup("P8_7", GPIO.OUT)
GPIO.setup("P8_9", GPIO.OUT)
GPIO.setup("P8_11", GPIO.OUT)
GPIO.setup("P8_15", GPIO.OUT)

# wlaczenie glosnika
PWM.start("P8_13", 25, 1000)

# zapalanie diod i gaszenie po wcisnieciu guzika
for i in range(5):
    rand = random.randrange(1, 5, 1)
    button = 1
    if rand == 1:
        GPIO.output("P8_7", GPIO.HIGH)
        while button == 1:
            button = GPIO.input("P8_8")
        while button == 0:
            button = GPIO.input("P8_8")
        GPIO.output("P8_7", GPIO.LOW)
    elif rand == 2:
        GPIO.output("P8_9", GPIO.HIGH)
        while button == 1:
            button = GPIO.input("P8_10")
        while button == 0:
            button = GPIO.input("P8_10")
        GPIO.output("P8_9", GPIO.LOW)
    elif rand == 3:
        GPIO.output("P8_11", GPIO.HIGH)
        while button == 1:
            button = GPIO.input("P8_12")
        while button == 0:
            button = GPIO.input("P8_12")
        GPIO.output("P8_11", GPIO.LOW)
    elif rand == 4:
        GPIO.output("P8_15", GPIO.HIGH)
        while button == 1:
            button = GPIO.input("P8_16")
        while button == 0:
            button = GPIO.input("P8_16")
        GPIO.output("P8_15", GPIO.LOW)
print("zakonzono")
PWM.stop("P8_13")
PWM.cleanup()
GPIO.cleanup()