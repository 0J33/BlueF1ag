import numpy as np
import datetime as dt
from time import time
from time import ctime
import fastf1 as ff1
import pathlib
import platform
from pymongo import MongoClient
import os
from dotenv import load_dotenv
platform.system()

load_dotenv()

connection_string = os.getenv("connection_string")
db_name = os.getenv("db_name")

client = MongoClient(connection_string)
db = client[db_name]

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
        for i in range(1950, dt.datetime.now().year+1):
            years.append(i)
    elif func == "constructors":
        for i in range(1958, dt.datetime.now().year+1):
            years.append(i)
    else:
        for i in range(2018, dt.datetime.now().year+1):
            years.append(i)
    return years[::-1]

### get races of a given year ###
def get_races(yr):
    collection_name = "races"
    collection = db[collection_name]
    doc = collection.find_one({"year": int(yr)})
    return doc["races"]

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
    res = []
    for i in range(1, max+1):
        res.append(i)
    return res

### gets distance of a session ###
def get_distance(yr, rc, sn):
    session = ff1.get_session(yr, rc, sn)
    session.load()
    laps = session.laps
    car_data = laps.pick_fastest().get_car_data().add_distance()
    maxdist = int(np.max(car_data['Distance']))
    res = []
    for i in range(0, maxdist+1, 100):
        res.append(i)
    res.append(maxdist)
    return res

### db ###

def get_races_from_db(func, yr):
    if func.lower() == "event":
        collection_name = "races"
        collection = db[collection_name]
        
        doc = collection.find_one({"year": int(yr)})
        races = doc["races"]

        res = []
        for race in races:
            if "testing" not in race.lower() and "pre-season" not in race.lower():
                res.append(race)
    else:
        collection_name = "data"
        collection = db[collection_name]
        docs = collection.find({"year": int(yr)})
        
        records = []
        for doc in docs:
            records.append(doc["race"])
        
        res = []
        for record in records:
            if record not in res:
                if "test" not in record.lower() and "pre-season" not in record.lower():
                    res.append(record)
    return res

def get_sessions_from_db(yr, rc):
    collection_name = "data"
    collection = db[collection_name]
    
    docs = collection.find({"year": int(yr), "race": rc})
    res = []
    for doc in docs:
        res.append(doc["session"])

    if int(yr) <= 2018:
        res = ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Race']
    return res

def get_drivers_from_db(yr, rc, sn):
    collection_name = "data"
    collection = db[collection_name]
    sn = sn.capitalize()
    doc = collection.find_one({"year": int(yr), "race": rc, "session": sn})
    drivers = doc["drivers"]
    drivers = sorted(drivers)
    return drivers

def get_laps_from_db(yr, rc, sn):
    collection_name = "data"
    collection = db[collection_name]
    sn = sn.capitalize()
    doc = collection.find_one({"year": int(yr), "race": rc, "session": sn})
    max_lap = doc["laps"]
    laps = []
    for i in range(1, max_lap+1):
        laps.append(i)
    return laps

def get_distance_from_db(yr, rc, sn):
    collection_name = "data"
    collection = db[collection_name]
    sn = sn.capitalize()
    doc = collection.find_one({"year": int(yr), "race": rc, "session": sn})
    max_dist = doc["distance"]
    dist = []
    for i in range(0, max_dist+1, 100):
        dist.append(i)
    dist.append(max_dist)
    return dist