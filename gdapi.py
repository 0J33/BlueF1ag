from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
import json
import os
import fastf1 as ff1
from fastf1 import plotting
import datetime as dt
import pandas as pd
from pymongo import MongoClient
# from update import *
from env import *
from utils import *

client = MongoClient(connection_string)
db = client[db_name]

# Define the scopes you need
SCOPES = ['https://www.googleapis.com/auth/drive']

# Create credentials from the service account JSON key file
credentials = service_account.Credentials.from_service_account_file(
    'creds_sc.json',
    scopes=SCOPES
)

# Set up Google Drive API client
drive_service = build('drive', 'v3', credentials=credentials)



### GOOGLE DRIVE API FUNCTIONS ###

# Upload JSON file to a specific folder
def upload_file_to_folder(file_name, folder_id):
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload("record_dump/" + file_name, mimetype='application/json')
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('File ID: %s' % uploaded_file.get('id'))

# Get the ID of the "Blue F1ag Storage" folder
def get_folder_id(folder_name):
    results = drive_service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                                          fields="files(id)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        print(f"Folder '{folder_name}' not found.")
        return None

# Download JSON file
def download_file(file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    fh = open("record_dump/" + file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print('Download %d%%.' % int(status.progress() * 100))
    fh.close()
        
# Save record as file
def save_record_as_file(record, file_name):
    if type(record) is not list:
        with open("record_dump/" + file_name, 'w') as f:
            json.dump(record, f, indent=4)
    else:
        with open("record_dump/" + file_name, 'w') as f:
            json.dump({"records": record}, f, indent=4)
        
# Read record from file
def read_record_from_file(file_name):
    with open("record_dump/" + file_name, 'r') as f:
        record = json.load(f)
    return record

# Get file ID
def get_file_id(file_name):
    results = drive_service.files().list(q=f"name='{file_name}' and parents in '{get_folder_id('Blue F1ag Storage')}'",
                                          fields="files(id)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        print(f"File '{file_name}' not found.")
        return None

# Delete file locally
def delete_file(file_name):
    os.remove("record_dump/" + file_name)

# Delete file from Google Drive
def delete_file_from_drive(file_id):
    drive_service.files().delete(fileId=file_id).execute()
    print(f"File '{file_id}' deleted.")

###

def save_laps(yr, rc, sn):
    
    file_name = f"{yr}_{rc}_{sn}_laps.json"
    
    try:
        
        if get_file_id(file_name) is not None:
            raise Exception("File already exists")
        
        if "test" in rc.lower() or "pre-season" in rc.lower():
            raise Exception("Test session")
        
        if rc == "Sprint Shootout":
            raise Exception("Sprint Shootout")
        
        if get_file_id(file_name) is None:

            session = get_sess(yr, rc, sn)
            session.load()
            laps = session.laps
            
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
                'laps': new_laps
            }
            
            save_record_as_file(record, file_name)
            blue_f1ag_folder_id = get_folder_id('Blue F1ag Storage')
            upload_file_to_folder(file_name, blue_f1ag_folder_id)
            delete_file(file_name)
            
    except Exception as exc:
        
        print("error", str(exc)) 

def save_telemetry(yr, rc, sn):
    
    file_name = f"{yr}_{rc}_{sn}_telemetry.json"
    
    try:
        
        if get_file_id(file_name) is not None:
            raise Exception("File already exists")
        
        if "test" in rc.lower() or "pre-season" in rc.lower():
            raise Exception("Test session")
        
        if rc == "Sprint Shootout":
            raise Exception("Sprint Shootout")

        session = get_sess(yr, rc, sn)
        session.load()
        laps = session.laps
        
        drivers = laps['Driver'].unique()
        # drivers = ['VER', 'ALO']
        
        all_telemetry = []
        
        for driver in drivers:
        
            lap = 1
            while lap <= 100:
            # while lap <= 2:
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
                
        all_records = []
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
                'driver': driver,
                'lap': lap,
                'telemetry': data_list
            }

            all_records.append(record)
            
        laps = []
            
        for driver in drivers:
            
            file_name_drv = f"{yr}_{rc}_{sn}_{driver}_telemetry.json"
            
            if get_file_id(file_name_drv) is not None:
                raise Exception("File already exists")
            
            driver_records = []
            for record in all_records:
                if record['driver'] == driver:
                    driver_records.append(record)
                    
            laps.append(driver_records[-1]['lap'])
            
            save_record_as_file(driver_records, file_name_drv)
            blue_f1ag_folder_id = get_folder_id('Blue F1ag Storage')
            upload_file_to_folder(f"{yr}_{rc}_{sn}_{driver}_telemetry.json", blue_f1ag_folder_id)
            delete_file(f"{yr}_{rc}_{sn}_{driver}_telemetry.json")
        
        all_records_drv = []
        i=0
        while i < len(drivers):
            try:
                record_temp = {
                    'driver': drivers[i],
                    'lap': laps[i]
                }
            except:
                record_temp = {
                    'driver': drivers[i],
                    'lap': None
                }
            all_records_drv.append(record_temp)
            i += 1
        
        save_record_as_file(all_records_drv, file_name)
        blue_f1ag_folder_id = get_folder_id('Blue F1ag Storage')
        upload_file_to_folder(file_name, blue_f1ag_folder_id)
        delete_file(file_name)

    except Exception as exc:
        
        print("error", str(exc)) 

def get_laps(yr, rc, sn):
    
    try:
    
        file_name = f"{yr}_{rc}_{sn}_laps.json"
        download_file(get_file_id(file_name), file_name)
        laps = read_record_from_file(file_name)
        delete_file(file_name)

        laps = laps['laps']
        laps = pd.DataFrame(laps)
        
        for col in laps.columns:
            if col.lower().__contains__("time"):
                laps[col] = pd.to_timedelta(laps[col])

        return laps
    
    except:
    
        return None

def get_telemetry(yr, rc, sn, driver, lap):
    
    try:
        
        file_name = f"{yr}_{rc}_{sn}_{driver}_telemetry.json"
        download_file(get_file_id(file_name), file_name)
        records = read_record_from_file(file_name)

        records = records['records']
        
        record = None
        for doc in records:
            if doc['driver'] == driver and doc['lap'] == lap:
                record = doc
                break
        delete_file(file_name)
        
        telemetry = record['telemetry']
        telemetry = pd.DataFrame(telemetry)
        
        for col in telemetry.columns:
            if col.lower().__contains__("time"):
                telemetry[col] = pd.to_timedelta(telemetry[col])

        return telemetry
    
    except:
        
        return None
    
### END OF GOOGLE DRIVE API FUNCTIONS ###


### TEMP FUNCTIONS ###

def save(yr, flag):
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
                save_laps(yr, rc, sn)
                print(f"{yr}_{rc}_{sn}.json saved")
                
            if flag == "telemetry":
                save_telemetry(yr, rc, sn)
                print(f"{yr}_{rc}_{sn}_telemetry.json saved")

def save_from(yr, flag):
    for yr in range(yr, dt.datetime.now().year + 1):
        save(yr, flag)
                                        
### END OF TEMP FUNCTIONS ###


#### FOR TESTING ###

# record = {'VER': 1, 'ALO': 2, 'PER': 3}
# file_name = 'VER,ALO,PER.json'
# save_record_as_file(record, file_name)
# blue_f1ag_storage_folder_id = get_folder_id('Blue F1ag Storage')
# upload_file_to_folder(file_name, blue_f1ag_storage_folder_id)
# delete_file(file_name)

# file_name = 'VER,ALO,PER.json'
# download_file(get_file_id(file_name), file_name)
# record = read_record_from_file(file_name)
# delete_file(file_name)
# print(record)

# done = False
# while(not done):
#     try:
#         save_from(2018, "telemetry")
#         done = True
#     except:
#         done = False

save_telemetry(2023, "Bahrain Grand Prix", "Qualifying")

### END OF TESTING ###