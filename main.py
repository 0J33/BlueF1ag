from flask import Flask
from threading import Thread
import asyncio
import os
import pathlib
import sys
import tracemalloc
import random
from flask import Blueprint, jsonify, request
import requests
import json
import seaborn as sns
import fastf1
from fastf1 import plotting
from fastf1 import utils
import fastf1.plotting
from fastf1.core import Laps
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import pandas as pd
from timple.timedelta import strftimedelta
from matplotlib.colors import ListedColormap
from matplotlib.collections import LineCollection
from matplotlib import cm
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator
import matplotlib.font_manager as fm
from time import time, ctime
import time as tm
from datetime import datetime
import datetime
from matplotlib import dates
from email.message import EmailMessage
import ssl
import smtplib
from env import *
from funcs import *
import warnings
import platform
warnings.filterwarnings("ignore", category=FutureWarning)
platform.system()
mpl.use('Agg')
pd.set_option('display.max_rows', None)

#set mpl font
set_font()

#enable cache
if os.path.exists(dir_path + get_path() + "doc_cache"):
    fastf1.Cache.enable_cache(dir_path + get_path() + "doc_cache")


queue = []

#delete files after sending
def delete(datetime):
    try:
        os.remove(dir_path + get_path() + "output" + get_path() + str(datetime) + '.png')
    except:
        pass
        
    try:
        os.remove(dir_path + get_path() + "output" + get_path() + str(datetime) + '.txt')         
    except:
        pass

#delete all files
def delete_all():
    for i in queue:
        delete(i)

#method that logs data from slash commands
def log(user_id, message, exc, flag, datetime):   
    if os.path.exists(dir_path + get_path() + "logs" + get_path() + "logs.txt"): 
        if ((user_id in IDS)):
            if flag:
                testf = open(dir_path + get_path() + "logs" + get_path() + "devexc.txt","a")
            else:
                testf = open(dir_path + get_path() + "logs" + get_path() + "devlogs.txt","a")
            testf.write(str(message) + "\n" + str(exc) + str(datetime) + "\n\n")
            testf.close()
        else:
            if flag:
                testf = open(dir_path + get_path() + "logs" + get_path() + "exc.txt","a") 
            else:
                testf = open(dir_path + get_path() + "logs" + get_path() + "logs.txt","a")
            testf.write(str(user_id) + "\n" + str(message) + "\n" + str(exc) + str(datetime) + "\n\n")
            testf.close()

#fix exception string
def fix_exc(exc, fixed_inputs, comm):
    
    yr = fixed_inputs[0]
    
    rcint = False
    
    try:
        rc = fixed_inputs[1]
        try:
            rc = int(rc)
            rcint = True
        except:
            pass
    except:
        pass
    
    #yr
    if exc.__contains__("The data you are trying to access has not been loaded yet.") and yr < 2018:
        exc = "The FastF1 API has data starting from 2018. Please make sure you provided all the inputs correctly and try again.\n"
    elif exc.__contains__("The data you are trying to access has not been loaded yet.") and yr >= datetime.datetime.now().year:
        try:
            sn = ""
            try:
                sn = " " + str(fixed_inputs[2])
            except:
                sn = ""
            if rcint:
                exc = "I can't find any F1 data for the requested grand prix (" + str(fixed_inputs[0]) + " Round " + str(rc) + sn + "). It may have not been loaded yet.\n"
            else:
                exc = "I can't find any F1 data for the requested grand prix (" + str(fixed_inputs[0]) + " " + str(rc) + sn + "). It may have not been loaded yet.\n"
        except:
            exc = "I can't find any F1 data for the requested Grand Prix. It may have not been loaded yet.\n"
    elif exc.__contains__("The data you are trying to access has not been loaded yet.") and (yr < datetime.datetime.now().year and yr >= 2018):
        try:
            if rcint:
                exc = "I can't find any F1 data for the requested grand prix (" + str(fixed_inputs[0]) + " Round " + str(rc) + ").\n"
            else:
                exc = "I can't find any F1 data for the requested grand prix (" + str(fixed_inputs[0]) + " " + str(rc) + ").\n"
        except:
            exc = "I can't find any F1 data for the requested Grand Prix.\n"
    elif exc.__contains__("list index out of range") or exc.__contains__("'code'") or exc.__contains__("integer division or modulo by zero"): 
        exc = "There requested data is not available for the year " + str(yr) + ".\n"
    elif exc.__contains__("invalid literal for int()"):
        exc = "I can't find the year " + str(yr) + ". Please make sure you provided all the inputs correctly and try again.\n"
    elif exc.__contains__("No such file or directory") and (comm == "drivers" or comm == "constructors"):
        exc = "There requested data is not available for the year " + str(yr) + ".\n"
        
    #rc
    elif exc.__contains__("cannot find race"):
        exc = "I can't find the requested race (" + str(rc) + "). Please make sure you provided all the inputs correctly and try again.\n"

    #sn
    elif exc.__contains__("Invalid session type"):
        exc = "I can't find the requested session (" + fixed_inputs[2] + "). Make sure to provide one of the following: FP1, FP2, FP3, Q, Sprint, R.\n"

    #driver
    elif exc.__contains__("Invalid driver identifier"):
        exc = "I can't find the requested driver(s). Make sure to provide a driver abbreviation, like 'VER' or 'LEC'.\n"
    
    #lap
    elif exc.__contains__("None of [Index") and exc.__contains__("are in the [columns]" and comm == "tires"):
        exc = "An error has occured. Try a different lap number\n"
        
    #other errors
    elif exc.__contains__("'NoneType' object is not subscriptable") or exc.__contains__("'NaTType' object has no attribute 'upper'") or exc.__contains__("0") or exc.__contains__ ("'Lap' object has no attribute 'session'") or exc.__contains__("No such file or directory") or exc.__contains__("attempt to get argmin of an empty sequence") or exc == "":
        exc = "An unknown error occured. Please make sure you provided all the command inputs correctly.\n"
        
    #connection error
    elif exc.__contains__("Cannot connect to host") or exc.__contains__("Unauthorized"):
        exc = "A connection error has occured. Please try again later.\n"
        
    #api error
    elif exc.__contains__("Expecting value: line 1 column 1 (char 0)"):
        exc = "An error occured while fetching data from the API. Please try again later.\n"
    
    #index
    elif exc.__contains__("single positional indexer is out-of-bounds"):
        exc = "Index is out-of-bounds.\n"
    
    else:
        exc = "An unknown error occured.\n"
    return exc


#send email
def send_email():

    try:
        from env import email_sender, email_password, email_reciever, server
    except:
        email_sender = os.getenv("MAIL")
        email_password = os.getenv("PASS")
        email_reciever = os.getenv("MAIL")
        server = os.getenv("SERVER")
        
    subject = "Backend"
    if server == "main":
        body = "Main backend server is online."
    else:
        body = "Backup backend server is online."

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_reciever
    em['Subject'] = subject

    context = ssl.create_default_context()
    
    em.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(
            email_sender, email_reciever,
            em.as_string())
        
    print("Email sent")

#command
def command(user_id, input_list, comm, datetime):
  
    try:
        
        message = ""
  
        fixed_inputs = []
        
        year = input_list[0]
        try:
            yr = int(year)
        except:
            yr = 0
        
        fixed_inputs.append(yr)
        
        if not(comm == "schedule" or comm == "drivers" or comm == "constructors"):
            race = input_list[1]
            try:
                rc = int(race)
            except:
                rc = race
                
            fixed_inputs.append(rc)
            
        if not(comm == "schedule" or comm == "event" or comm == "drivers" or comm == "constructors" or comm == "strategy" or comm == "racetrace"):    
            session = input_list[2]
            sn = session.upper()
            if(sn=="Q1" or sn=="Q2" or sn=="Q3" or sn=="QUALI"):
                sn = "Q"
                
            fixed_inputs.append(sn)
        
        if (comm == "laps" or comm == "time" or comm == "distance" or comm == "racetrace"):
            if (comm == "racetrace"):
                driver_list = input_list[2]
            else:
                driver_list = input_list[3]
                
            drivers = []
            
            i=0
            driver=""
            while(i<len(driver_list)):
                if(driver_list[i]!=' '):
                    driver = driver + driver_list[i]
                    i=i+1
                else:
                    driver = driver.upper()[:3]
                    drivers.append(driver[:3])
                    driver = ""
                    i=i+1
            driver = driver.upper()[:3]
            drivers.append(driver[:3])
            driver = ""
        
            fixed_inputs.append(drivers)
        
        if (comm == "gear" or comm == "speed"):
            driver = input_list[3]
            
            if driver != None:
                driver = driver.upper()[:3]
            
            fixed_inputs.append(driver)
        
        if (comm == "delta" or comm == "telemetry" or comm == "cornering" or comm == "sectors"):    
            driver1 = input_list[3]
            driver2 = input_list[4]
            d1 = driver1[:3]
            d2 = driver2[:3]

            d1 = d1.upper()
            d2 = d2.upper()
            
            fixed_inputs.append(d1)
            fixed_inputs.append(d2)
        
        if (comm == "cornering"):
            distance1 = input_list[5]
            distance2 = input_list[6]
            dist_err = ""
            
            try:
              
              if distance1 == None:
                dist1 = 0
              else:
                dist1 = int(distance1)
                
              if distance2 == None:
                dist2 = 0 
              else:
                dist2 = int(distance2)
                
              if(dist1<0):
                dist_err = "Negative numbers not allowed. (Using 0 instead)"
                dist1=0
                
              if(dist2<0):
                dist_err = "Negative numbers not allowed. (Using 0 instead)"
                dist2=0
                
            except:
              dist1 = 0
              dist2 = 0
              dist_err = "\n\n Distance 1 or Distance 2 was invalid. Please enter a valid number.\n(0, 0) Distance used instead."
              
            if(dist1>dist2):
                dist_err = "Distance 1 must be smaller than Distance 2.\nSwapping distance instead."
                temp = dist1
                dist1 = dist2
                dist2 = temp
                
            if(dist1==dist2):
                dist_err = "Distance 1 must be smaller than Distance 2.\nUsing 0 for Distance 1 instead."
                dist1 = 0
            
            fixed_inputs.append(dist1)
            fixed_inputs.append(dist2)
            
        if (comm == "time" or comm == "distance" or comm == "gear" or comm == "speed" or comm == "tires"):
            if (comm == "tires"):
                lap = input_list[3]
            else:
                lap = input_list[4]
            
            if (lap != None):
                try:
                    lap=int(lap)
                    if(lap<=0):
                        lap = 1
                except:
                    lap = 1
        
            fixed_inputs.append(lap)
            
        if (comm == "delta" or comm == "telemetry" or comm == "cornering" or comm == "sectors"):
            if (comm == "cornering"):
                lap1 = input_list[7]
                lap2 = input_list[8]
            else:
                lap1 = input_list[5]
                lap2 = input_list[6]
            
            if (lap1 != None):
                try:
                    lap1=int(lap1)
                    if(lap1<=0):
                        lap1 = 1
                except:
                    lap1 = 1
            
            if (lap2 != None):
                try:
                    lap2=int(lap2)
                    if(lap2<=0):
                        lap2 = 1
                except:
                    lap2 = 1
                
            fixed_inputs.append(lap1)
            fixed_inputs.append(lap2)

        inputs = ""
        for i in range(len(fixed_inputs)):
            inputs = inputs + " " + str(fixed_inputs[i])
        message = "/" + comm + inputs

        log(user_id, message, "", False, datetime)

        if comm == "fastest":
            fastest_func(fixed_inputs, datetime)
        elif comm == "results":
            results_func(fixed_inputs, datetime)
        elif comm == "schedule":
            schedule_func(fixed_inputs, datetime)
        elif comm == "event":
            event_func(fixed_inputs, datetime)
        elif comm == "laps":
            laps_func(fixed_inputs, datetime)
        elif comm == "time":
            time_func(fixed_inputs, datetime)
        elif comm == "distance":
            distance_func(fixed_inputs, datetime)
        elif comm == "delta":
            delta_func(fixed_inputs, datetime)
        elif comm == "gear":
            gear_func(fixed_inputs, datetime)
        elif comm == "speed":
            speed_func(fixed_inputs, datetime)
        elif comm == "telemetry":
            tel_func(fixed_inputs, datetime)
        elif comm == "cornering":
            cornering_func(fixed_inputs, datetime)
        elif comm == "tires":
            tires_func(fixed_inputs, datetime)
        elif comm == "strategy":
            strategy_func(fixed_inputs, datetime)
        elif comm == "sectors":
            sectors_func(fixed_inputs, datetime)
        elif comm == "racetrace":
            rt_func(fixed_inputs, datetime)
    
        if os.path.exists(dir_path + get_path() + "logs" + get_path() + "logs.txt"): 
            print("FINISHED " + message + " " + datetime)
    
    except Exception as exc:
        
        exc = str(exc)
        
        if os.path.exists(dir_path + get_path() + "logs" + get_path() + "logs.txt"): 
            print(exc)
        
        log(user_id, message, exc + "\n", True, datetime)
        exc = fix_exc(exc, fixed_inputs, comm)
        
        return exc

    queue.append(datetime)
    return datetime

#flask server
app = Flask('', static_folder='res')

@app.route('/', methods=['GET', 'POST'])
def home():
        
    if request.method == 'POST':

        try:
                
            print(request.form)
            
            func_name = request.form.get('func_name')
            datetime = request.form.get('datetime')
            input_list = request.form.get('input_list')
            user_id = request.form.get('id')
            input_list = input_list.replace("[", "").replace("]", "").replace("'", "").split(', ')
            print(input_list)
            print(func_name)
            if not (func_name.lower() == "drivers" or func_name.lower() == "constructors"):
                result = "/res/output/" + command(user_id, input_list, func_name.lower(), datetime) + ".png"
            else:
                try:
                    result = "/res/stnd/" + str(input_list[0]) + "_" + str(func_name).upper() + "_STANDINGS.png"
                    log(user_id, str(func_name) + "\n" + str(input_list), "", False, datetime)
                except Exception as exc:
                    print(str(exc))
                    log(user_id, str(func_name) + "\n" + str(input_list), str(exc), True, datetime)
            return jsonify({'result': result}), 200    
        except Exception as exc:
            return jsonify({'error': str(exc)}), 400
        
    else:
        return ("Backend is running.")
    
def run():
  app.run(host='0.0.0.0',port=2222)
  send_email()
  delete_all()

def keep_alive():
    t = Thread(target=run)
    t.start()
    
keep_alive()