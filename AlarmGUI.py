# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 13:45:24 2019

@author: Krzysztof Pasiewicz
"""
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
 
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
    if request.form['username'] == 'admin':
        session['logged_in'] = True
        user = request.form['username']
    else:
        flash('wrong password!')
    return home()

@app.route('/toset')
def passSet():
    return render_template('Set.html')
    

@app.route('/set', methods=['POST'])
def setAlarm():
    print(request.form['hours'])
    print(type(request.form['hours']))
    print(request.form['minutes'])
    return home()
    

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)