# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 13:45:24 2019

@author: Krzysztof Pasiewicz
"""
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import sqlite3

db = sqlite3.connect('baza.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS alarmy(id INT PRIMARY KEY,user TEXT, godzina INT, minuty INT);')

app = Flask(__name__)

 
@app.route('/')
def home():
    global user
    if not session.get('logged_in'):
        return render_template('newLogin.html')
    else:
        return render_template('Main.html', username=user)
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    global user
    #session['logged_in'] = False
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
    hour = request.form['hours']
    minute = request.form['minutes']
    if hour and minute:
        hour = int(hour)
        minute = int(minute)
        """print(hour)
        print(type(hour))
        print(minute)"""
        if hour > 0 and hour < 24 and minute > 0 and minute < 60:
            print(hour)
            print(type(hour))
            print(minute)
            cursor.execute('SELECT MAX(id) FROM alarmy;')
            id_val = cursor.fetchall()
            id_val = id_val + 1
            cursor.execute('INSERT INTO alarmy VALUES(?,?,?,?);',(id_val,user, hour, minute))
            #set alarm time and add to database here TODO
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
    app.run(debug=True,host='0.0.0.0', port=4000)