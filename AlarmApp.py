# -*- coding: utf-8 -*-
"""
Created on Jan 23 15:00:15 2019

@author: Pasiewicz, Frankowski, Szyszka
"""
from flask import Flask, flash, redirect, render_template, request, session, abort, g
import os
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import sqlite3
from threading import Thread
from time import sleep
from RTC import *
import random

DATABASE = 'baza.db'
alarm_thread = None
activated_alarm = -1

ds = DS1307(2, 0x68)
ds.write_all(30,30,10,3,30,1,19)

# inicjalizacja
GPIO.setup("P8_8", GPIO.IN)
GPIO.setup("P8_10", GPIO.IN)
GPIO.setup("P8_12", GPIO.IN)
GPIO.setup("P8_16", GPIO.IN)

GPIO.setup("P8_7", GPIO.OUT)
GPIO.setup("P8_9", GPIO.OUT)
GPIO.setup("P8_11", GPIO.OUT)
GPIO.setup("P8_15", GPIO.OUT)


def do_noise():
    PWM.start("P8_13", 25, 1000)

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


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def time_check(hour, minute, stop):
    # activate alarm on Beagle TODO
    global thread_stop
    while True:
        print(hour)
        print(minute)
        if hour == ds._read_hours() and minute == ds._read_minutes():
            #do_noise()
            print('ALARMALARMALARMALARM#############################################')
            thread_stop = True
        if stop():
            print("  Exiting loop.")
            break


# db = sqlite3.connect('baza.db')
# global cursor
# cursor = db.cursor()
# cursor.execute('CREATE TABLE IF NOT EXISTS alarmy(id INT PRIMARY KEY,user TEXT, godzina INT, minuty INT);')

app = Flask(__name__)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Tutaj musicie zwrócić alarmy dla użytkownika w formacie id|hour|active;
# Tylko dla aktywnego użytkownika
# ostatni alarm bez średnika !!
@app.route("/getAlarms")
def getAlarms():
    global user
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM alarmy WHERE user =  ?;', (user,))
    alarms = cursor.fetchall()
    output = ""
    for alarm in alarms:
        output = output + str(alarm[0]) + "|" + str(alarm[2]) + "." + str(alarm[3]) + "|0;"
    output = output[:-1]
    return output


# usuwanie alarmu, na wejściu dostajecie jego id, jak się powiedzie zwracacie "ok", jak nie to "false";
@app.route('/deleteAlarm', methods=['GET'])
def drop_alarm():
    global alarm_thread
    alarmID = request.args.get('alarmID')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM alarmy WHERE id =  ?;', (alarmID,))
    print(alarmID)
    return "ok"


# też zwracacie ok jak się uda
@app.route('/disactivateAlarm', methods=['GET'])
def disactivate_alarm():
    global thread_stop
    global activated_alarm
    alarmID = request.args.get('alarmID')
    print(alarmID)
    thread_stop = True
    alarm_thread.join()
    activated_alarm = -1
    return "ok"


# też zwracacie ok jak się uda
@app.route('/activateAlarm', methods=['GET'])
def activate_alarm():
    global alarm_thread
    global thread_stop
    global activated_alarm
    thread_stop = False
    alarmID = request.args.get('alarmID')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM alarmy WHERE id =  ?;', (alarmID,))
    alarm = cursor.fetchall()
    hour = alarm[0][2]
    minute = alarm[0][3]
    #print(hour)
    #print(minute)
    activated_alarm = int(alarmID)
    alarm_thread = Thread(target=time_check, args=(hour, minute, lambda: thread_stop))
    alarm_thread.start()
    return "ok"


@app.route('/')
def home():
    global user
    db = get_db()
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS alarmy(id INT PRIMARY KEY,user TEXT, godzina INT, minuty INT);')
    """cursor.execute('SELECT * FROM alarmy;')
    id_val = cursor.fetchall()
    print(id_val)
    cursor.execute('INSERT INTO alarmy VALUES(?,?,?,?);',(1,'admin', 10, 24))
    cursor.execute('INSERT INTO alarmy VALUES(?,?,?,?);',(2,'admin', 12, 24))
    cursor.execute('INSERT INTO alarmy VALUES(?,?,?,?);',(3,'admin', 13, 24))
    cursor.execute('SELECT * FROM alarmy;')
    db.commit()
    id_val = cursor.fetchall()
    print(id_val)
    cursor.execute('SELECT MAX(id) FROM alarmy;')
    id_val = cursor.fetchall()
    print(id_val)"""
    if not session.get('logged_in'):
        return render_template('newLogin.html')
    else:
        return render_template('Main.html', username=user, time=str(ds._read_hours()) + ":" + str(ds._read_minutes()))


@app.route('/refresh')
def refresh():
    print(ds._read_hours())
    print(ds._read_minutes())
    return str(ds._read_hours()) + ":" + str(ds._read_minutes())
    # return render_template('Main.html', username=user, hour = time1, minute = time2)


@app.route('/tomain')
def go_back():
    global user
    return render_template('Main.html', username=user, time=str(ds._read_hours()) + ":" + str(ds._read_minutes()))


@app.route('/login', methods=['POST'])
def do_admin_login():
    global user
    # session['logged_in'] = False
    if request.form['username']:
        session['logged_in'] = True
        user = request.form['username']
    else:
        flash('no user!')
    return home()


@app.route('/toset')
def passSet():
    return render_template('Set.html')


@app.route('/set', methods=['POST'])
def setAlarm():
    global user
    global alarm_thread
    global thread_stop
    global activated_alarm
    thread_stop = False
    hour = request.form['hours']
    minute = request.form['minutes']
    if hour and minute:
        hour = int(hour)
        minute = int(minute)
        if hour > 0 and hour < 24 and minute > 0 and minute < 60:
            #            print(hour)
            #            print(type(hour))
            #            print(minute)
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT MAX(id) FROM alarmy;')
            id_val = cursor.fetchall()
            print(id_val[0][0])
            if id_val[0][0] is not None:
                id_out = id_val[0][0] + 1
            else:
                id_out = 1
            cursor.execute('INSERT INTO alarmy VALUES(?,?,?,?);', (id_out, user, hour, minute))
            db.commit()
            activated_alarm = id_out
            # set alarm time and add to database here TODO
            alarm_thread = Thread(target=time_check, args=(hour, minute, lambda: thread_stop))
            alarm_thread.start()
        else:
            flash('wrong time format!')
    else:
        flash('no data detected!')
    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=4000)



