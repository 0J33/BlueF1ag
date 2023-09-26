import fastf1 as ff1
from pymongo import MongoClient
import json
import pandas as pd
import datetime
from datetime import datetime, timedelta
import os
try:
    from env import *
except:
    connection_string = os.getenv("connection_string")
    db_name = os.getenv("db_name")
from utils import *

client = MongoClient(connection_string)
db = client[db_name]

### MONGO FUNCTIONS ###

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

def save_laps(yr, rc, sn):
    
    collection = db['laps']
    
    try:
        
        if "test" in rc.lower():
            raise Exception("Test session")
        
        if rc == "Sprint Shootout":
            raise Exception("Sprint Shootout")
        
        if collection.count_documents({'yr': yr, 'rc': rc, 'sn': sn}) == 0:

            session = get_sess(yr, rc, sn)
            laps = session.load()
            
            new_laps = []
            
            for i in range(len(laps)):
                lap = laps.iloc[i].to_dict()
                for key in lap:
                    try:
                        json.dumps(lap[key])
                    except:
                        lap[key] = str(lap[key])
                print(yr, rc, sn, i+1, "/", len(laps))
                new_laps.append(lap)
                    
            if new_laps == []:
                raise Exception("No laps found")
                    
            record = {
                'yr': yr,
                'rc': rc,
                'sn': sn,
                'laps': new_laps
            }
            
            collection.insert_one(record)
            
    except:
        
        collection.insert_one({
            'yr': yr,
            'rc': rc,
            'sn': sn,
            'laps': []
        })

def save_telemetry(yr, rc, sn):
    
    collection = db['telemetry']
    
    try:
        
        if "test" in rc.lower():
            raise Exception("Test session")
        
        if rc == "Sprint Shootout":
            raise Exception("Sprint Shootout")

        session = get_sess(yr, rc, sn)
        laps = session.load()
        
        # drivers = laps['Driver'].unique()
        drivers = ['VER', 'ALO']
        
        all_telemetry = []
        
        for driver in drivers:
        
            lap = 1
            # while lap <= 100:
            while lap <= 2:
                try:
                    driver_laps = session.laps.pick_driver(driver)
                    fast = driver_laps[driver_laps['LapNumber'] == int(lap)].iloc[0]
                    telemetry = fast.get_car_data().add_distance()
                    
                    pos_data = fast.get_pos_data(pad=1, pad_side='both')
                    car_data = fast.get_car_data(pad=1, pad_side='both')
                    drv_ahead = car_data.iloc[1:-1].add_driver_ahead() \
                        .loc[:, ('DriverAhead', 'DistanceToDriverAhead',
                                'Date', 'Time', 'SessionTime')]
                    car_data = car_data.add_distance().add_relative_distance()
                    car_data = car_data.merge_channels(drv_ahead)
                    merged = pos_data.merge_channels(car_data)
                    new_merged = merged.slice_by_lap(fast, interpolate_edges=True)
                    telemetry = telemetry.merge_channels(new_merged)
                    
                    all_telemetry.append([driver, lap, telemetry])
                except:
                    pass
                lap += 1

        for driver, lap, tel in all_telemetry:
            data_list = []
            
            for _, row in tel.iterrows():
                temp = row.to_dict()
                for key in temp:
                    try:
                        json.dumps(temp[key])
                    except:
                        temp[key] = str(temp[key])
                data_list.append(temp)
        
            record = {
                'yr': yr,
                'rc': rc,
                'sn': sn,
                'driver': driver,
                'lap': lap,
                'telemetry': data_list
            }
            
            if collection.count_documents({'yr': yr, 'rc': rc, 'sn': sn, 'driver': driver, 'lap': lap}) == 0:
                collection.insert_one(record)

    except Exception as exc:
        
        print("error", str(exc)) 

def get_laps(yr, rc, sn):
    
    collection_name = "laps" ### CHANGE COLLECTION NAME HERE ###
    collection = db[collection_name]
    
    if collection.count_documents({'yr': yr, 'rc': rc, 'sn': sn}) == 1:
        doc = collection.find_one({'yr': yr, 'rc': rc, 'sn': sn})
        laps = doc['laps']
        laps = pd.DataFrame(laps)
        
        for col in laps.columns:
            if col.lower().__contains__("time"):
                laps[col] = pd.to_timedelta(laps[col])

        return laps
    
    else:
        
        return None

def get_telemetry(yr, rc, sn, driver, lap):
    
    collection_name = "telemetry" ### CHANGE COLLECTION NAME HERE ###
    collection = db[collection_name]
    
    if collection.count_documents({'yr': yr, 'rc': rc, 'sn': sn, 'driver': driver, 'lap': int(lap)}) == 1:
        doc = collection.find_one({'yr': yr, 'rc': rc, 'sn': sn, 'driver': driver, 'lap': int(lap)})
        telemetry = doc['telemetry']
        telemetry = pd.DataFrame(telemetry)
        
        for col in telemetry.columns:
            if col.lower().__contains__("time"):
                telemetry[col] = pd.to_timedelta(telemetry[col])

        return telemetry
    
    else:
        
        return None
    
### END OF MONGO FUNCTIONS ###


### TEMP FUNCTIONS ###

def save(flag):
    for yr in range(2018, datetime.datetime.now().year + 1):
        races_list = []
        collection_name = "races"
        collection = db[collection_name]
        docs = collection.find({"year": int(yr)})
        for doc in docs:
            races_list.append(doc['races'])
        races_list = races_list[0]
        for rc in races_list:
            rc = rc.strip()
            sessions = get_sessions(yr, rc)
            for sn in sessions:
                
                if flag == "laps":
                    collection_name = "laps"
                    collection = db[collection_name]
                    save_laps(yr, rc, sn)
                    print("laps", yr, rc, sn)
                    
                if flag == "telemetry":
                    collection_name = "telemetry"
                    collection = db[collection_name]
                    save_telemetry(yr, rc, sn)
                    print("telemetry", yr, rc, sn)
                    
### END OF TEMP FUNCTIONS ###