from functools import reduce
import numpy as np
from datetime import datetime, timedelta
from time import time
from time import ctime
import fastf1 as ff1
from fastf1 import utils
import pathlib
import platform
platform.system()

### UTIL FUNCTIONS ###

# get_datetime helper
def get_time():
    return ctime(time())

# get current time
def get_datetime():
    datetime = get_time()
    datetime = datetime.replace(" ", "-")
    datetime = datetime.replace(":", ".")
    return datetime

# get parth of file
dir_path = r"" + str(pathlib.Path(__file__).parent.resolve())

# get path for os
def get_path():
    if platform.system().__contains__("Win"):
        path = "\\"
    elif platform.system().__contains__("Lin"):
        path = "/"
    return path

# load the session
def get_sess(yr, rc, sn):
    
    #if session number
    try:
        rc = int(rc)
        session = ff1.get_session(yr, rc, sn)
    #if session not number
    except:
        try:
            #check if test
            if rc.lower().__contains__("preseason") or rc.lower().__contains__("pre-season") or rc.lower().__contains__("pre season") or rc.lower().__contains__("testing") or rc.lower().__contains__("test"):
                try:
                    session = ff1.get_testing_session(yr, 1, sn)
                except:
                    session = ff1.get_testing_session(yr, 2, sn)
            #not test
            else:
                session = ff1.get_session(yr, rc, sn)
        except:
            session = ff1.get_session(yr, rc, sn)
    session.load()
    try:
        fix = session.laps.pick_fastest()
    except:
        pass
    return session

# enable cache
try:
    ff1.Cache.enable_cache("doc_cache")
except: 
    pass

###

### gets the years for which data is available for each function ###
def get_years(func):
    years = []
    func = func.lower()
    if func == "results" or func == "schedule" or func == "drivers":
        for i in range(1950, datetime.datetime.now().year+1):
            years.append(i)
    elif func == "constructors":
        for i in range(1958, datetime.datetime.now().year+1):
            years.append(i)
    else:
        for i in range(2018, datetime.datetime.now().year+1):
            years.append(i)
    return years[::-1]

### get races of a given year ###
def get_races(yr):
    file = open("res/data.txt", "r")
    text = file.read()
    file.close()
    records = text.split("\n")
    res = ""
    for record in records:
        if record.__contains__(str(yr)):
            res = record[5:].split(",")
    for i in range(len(res)):
        res[i] = res[i].strip()
    return res

### gets sessions of a grand prix weekend ###
def get_sessions(yr, rc):
    yr = int(yr)
    sessions = []
    i=1
    while True:
        sess = 'Session' + str(i)
        fastf1_obj = ff1.get_event(yr, rc)
        try: 
            sessions.append((getattr(fastf1_obj, sess)))
        except:
            break
        i+=1
    return sessions
 
### gets drivers of a session ###
def get_drivers(yr, rc, sn):
    session = ff1.get_session(yr, rc, sn)
    session.load()
    laps = session.laps
    ls = set(tuple(x) for x in laps[['Driver']].values.tolist())
    lis = [x[0] for x in ls]
    return lis

### gets laps of a session ###
def get_laps(yr, rc, sn):
    session = ff1.get_session(yr, rc, sn)
    session.load()
    laps = session.laps
    ls = set(tuple(x) for x in laps[['LapNumber']].values.tolist())
    lis = sorted([int(x[0]) for x in ls])
    max = int(np.max(lis))
    return max

### gets distance of a session ###
def get_distance(yr, rc, sn):
    session = ff1.get_session(yr, rc, sn)
    session.load()
    laps = session.load()
    car_data = laps.pick_fastest().get_car_data().add_distance()
    maxdist = int(np.max(car_data['Distance']))
    return maxdist
