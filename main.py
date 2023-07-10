import aiohttp
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
from datetime import datetime as dt
import datetime
from matplotlib import dates
from email.message import EmailMessage
import ssl
import smtplib
from pymongo import MongoClient
from env import *
from funcs import *
import warnings
import platform
warnings.filterwarnings("ignore", category=FutureWarning)
platform.system()
mpl.use('Agg')
pd.set_option('display.max_rows', None)

# set mpl font
set_font()

# enable cache
if os.path.exists(dir_path + get_path() + "doc_cache"):
    fastf1.Cache.enable_cache(dir_path + get_path() + "doc_cache")

# delete all files
def delete_all():
    folder_path = dir_path + get_path() + "res" + get_path() + "output"
    # Get a list of all files in the folder
    file_list = os.listdir(folder_path)
    # Loop through each file and delete it
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        os.remove(file_path)

# method that logs data from slash commands
def log(user_id, message, exc, flag, datetime):  
    datetime = datetime.replace("-", " ").replace(".", ":")
    
    id_flg = False
    for i in IDS:
        if i in user_id:
            id_flg = True
            break
    if (not id_flg and not flag):
        collection_name = "logs"
    elif (not id_flg and flag):
        collection_name = "exc"
    elif (user_id in IDS and not flag):
        collection_name = "devlogs"
    elif (user_id in IDS and flag):
        collection_name = "devexc"
        
    client = MongoClient(connection_string)
    db = client[db_name]
    collection = db[collection_name]
        
    inputs = message.split(" ")[-1]
    comm = message.replace(inputs, "").strip()
    
    if not exc:
        collection.insert_one({
            "user_id": user_id, 
            "command": comm,
            "inputs": inputs,
            "datetime": datetime})
    else:
        collection.insert_one({
            "user_id": user_id, 
            "command": comm,
            "exception": exc,
            "inputs": inputs,
            "datetime": datetime,
        })

# fix exception string
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
    elif exc.__contains__("'NoneType' object is not subscriptable") or exc.__contains__("'NaTType' object has no attribute 'upper'") or exc.__contains__("single positional indexer is out-of-bounds") or exc=="0" or exc.__contains__ ("'Lap' object has no attribute 'session'") or exc.__contains__("No such file or directory") or exc.__contains__("attempt to get argmin of an empty sequence") or exc == "":
        exc = "An unknown error occured. Please make sure you provided all the command inputs correctly.\n"
        
    #connection error
    elif exc.__contains__("Cannot connect to host") or exc.__contains__("Unauthorized") or exc.__contains__("HTTP"):
        exc = "A connection error has occured. Please try again later.\n"
        
    #api error
    elif exc.__contains__("Expecting value: line 1 column 1 (char 0)"):
        exc = "An error occured while fetching data from the API. Please try again later.\n"
    
    else:
        exc = "An unknown error occured.\n"
    return exc

# command
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
            driver_list = []
            if (comm == "racetrace"):
                # driver_list = input_list[2]
                i = 2
            else:
                # driver_list = input_list[3]
                i = 3
                
            while i < len(input_list):
                if (input_list[i].isnumeric()):
                    break
                else:
                    driver_list.append(input_list[i])
                i+=1
                
            if driver_list[0].__contains__("/"):
                drivers = driver_list[0].split("/")
            else:
                drivers = driver_list
        
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
        
        print("STARTED " + message + " " + datetime)

        if comm == "fastest":
            res = fastest_func(fixed_inputs, datetime)
        elif comm == "results":
            res = results_func(fixed_inputs, datetime)
        elif comm == "schedule":
            res = schedule_func(fixed_inputs, datetime)
        elif comm == "event":
            res = event_func(fixed_inputs, datetime)
        elif comm == "laps":
            res = laps_func(fixed_inputs, datetime)
        elif comm == "time":
            res = time_func(fixed_inputs, datetime)
        elif comm == "distance":
            res = distance_func(fixed_inputs, datetime)
        elif comm == "delta":
            res = delta_func(fixed_inputs, datetime)
        elif comm == "gear":
            res = gear_func(fixed_inputs, datetime)
        elif comm == "speed":
            res = speed_func(fixed_inputs, datetime)
        elif comm == "telemetry":
            res = tel_func(fixed_inputs, datetime)
        elif comm == "cornering":
            res = cornering_func(fixed_inputs, datetime)
        elif comm == "tires":
            res = tires_func(fixed_inputs, datetime)
        elif comm == "strategy":
            res = strategy_func(fixed_inputs, datetime)
        elif comm == "sectors":
            res = sectors_func(fixed_inputs, datetime)
        elif comm == "racetrace":
            res = rt_func(fixed_inputs, datetime)
            
        if res !="success" or res == None:
            raise Exception("Internal Server Error. Please try again.")
        else:
            print("FINISHED " + message + " " + datetime)
                
            exc = ""
            flag = False
    
    except Exception as exc:
        
        exc = str(exc)
        flag = True
        
        if os.path.exists(dir_path + get_path() + "logs" + get_path() + "logs.txt"): 
            print(exc)
            
        exc = fix_exc(exc, fixed_inputs, comm)
        
        raise Exception(exc)

    log(user_id, message, exc, flag, datetime)
    return datetime

# flask server
app = Flask('', static_folder='res')

# update data
@app.route('/update', methods=['GET', 'POST'])
def update():
    yr = dt.now().year
    stnd = ""
    races = ""
    data = ""
    try:
        # PY is string like "py stnd.py" or "python stnd.py", etc.
        os.system(PY)
        stnd = "stnd success"
    except:
        stnd = "stnd fail"
    try:
        update_races(yr)
        races = "race success"
    except:
        races = "races fail"
    try:
        data = update_data(yr)
    except:
        data = "data fail"
    return stnd + "<br />" + races + "<br />" + data

# execute function when user submits form
@app.route('/', methods=['GET', 'POST'])
def home():
        
    if request.method == 'POST':

        try:
            func_name = request.form.get('func_name')
            datetime = request.form.get('datetime')
            input_list = request.form.get('input_list')
            user_id = request.form.get('id')
            input_list = input_list.replace("[", "").replace("]", "").replace("'", "").split(', ')
            for i in range(len(input_list)):
                if input_list[i] == "None":
                    input_list[i] = None
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
        return "Backend is running."

# run the server
def run():
    try:
        delete_all()
    except:
        pass
    app.run(host='0.0.0.0',port=2222)

# keep the server running
def keep_alive():
    t = Thread(target=run)
    t.start()

# keep the server running
keep_alive()