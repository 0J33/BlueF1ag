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

# Delete folder
def delete_folder(folder_name):
    results = drive_service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'", fields="files(id)").execute()
    items = results.get('files', [])
    for item in items:
        delete_file_from_drive(item['id'])

# Check if folder exists
def check_if_folder_exists(folder_name):
    results = drive_service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'", fields="files(id)").execute()
    items = results.get('files', [])
    if items:
        return True
    else:
        return False

# Check if file exists in folder
def check_file_in_folder(file_name, folder_name):
    folder_id = get_folder_id(folder_name)
    if folder_id is None:
        return False
    results = drive_service.files().list(q=f"name='{file_name}' and parents in '{folder_id}'",
                                          fields="files(id)").execute()
    items = results.get('files', [])
    if items:
        return True
    else:
        return False

# Upload csv file to a specific folder
def upload_file_to_folder(full_name, folder_id):
    if full_name.__contains__("/"):
        folder_name = full_name.split("/")[0]
        file_name = full_name.split("/")[1]
    else:
        file_name = full_name
        folder_name = "Blue F1ag"
    if check_file_in_folder(file_name, folder_name):
        print(f"File '{file_name}' already exists in folder '{folder_name}'.")
        return
    file_metadata = {'name': file_name, 'parents': [folder_id]}
    media = MediaFileUpload("record_dump/" + full_name, mimetype='application/json')
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('File ID: %s' % uploaded_file.get('id'))

# Get the ID of the "Blue F1ag" folder
def get_folder_id(folder_name):
    results = drive_service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                                          fields="files(id)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        print(f"Folder '{folder_name}' not found.")
        return None

# Get folder name using ID
def get_folder_name(folder_id):
    results = drive_service.files().list(q=f"id='{folder_id}' and mimeType='application/vnd.google-apps.folder'",
                                          fields="files(name)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['name']
    else:
        print(f"Folder '{folder_id}' not found.")
        return None

# Download csv file
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
def save_record_as_file(csv, file_name):
    with open("record_dump/" + file_name, 'w') as f:
        for i in csv:
            for j in i:
                f.write(str(j) + ",")
            f.write("\n")
        
# Read record from file
def read_record_from_file(file_name):
    with open("record_dump/" + file_name, 'r') as f:
        csv = f.read()
    return csv

# Get file ID
def get_file_id(file_name, folder_name):
    results = drive_service.files().list(q=f"name='{file_name}' and parents in '{get_folder_id(folder_name)}'",
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

# Create folder
def create_folder(parent_folder_name, subfolder_name):
    parent_folder_id = get_folder_id(parent_folder_name)  # You need to implement get_folder_id function
    if parent_folder_id is None:
        print(f"Parent folder '{get_folder_id(parent_folder_name)}' not found.")
        return

    file_metadata = {
        'name': subfolder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }

    try:
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        print(f"Subfolder '{subfolder_name}' created with ID: {folder.get('id')}")
        return folder.get('id')
    except Exception as e:
        print(f"An error occurred: {e}")

###

def save_laps(yr, rc, sn):
    
    file_name = f"{yr}_{rc}_{sn}_laps.csv"
    
    try:
        
        if get_file_id(file_name, 'Blue F1ag') is not None:
            raise Exception("File already exists")
        
        if "test" in rc.lower() or "pre-season" in rc.lower():
            raise Exception("Test session")
        
        if rc == "Sprint Shootout":
            raise Exception("Sprint Shootout")
        
        if get_file_id(file_name, "Blue F1ag") is None:

            session = get_sess(yr, rc, sn)
            session.load()
            laps = session.laps
            
            titles = []
            for i in laps.columns:
                if i not in titles:
                    titles.append(i)
                    
            new_laps = []
            new_laps.append(titles)
            
            for i in range(len(laps)):
                lap = laps.iloc[i]
                new_lap = []
                for j in titles:
                    new_lap.append(lap[j])
                new_laps.append(new_lap)
            
            if new_laps == []:
                raise Exception("No laps found")
            
            save_record_as_file(new_laps, file_name)
            blue_f1ag_folder_id = get_folder_id('Blue F1ag')
            upload_file_to_folder(file_name, blue_f1ag_folder_id)
            delete_file(file_name)
            
    except Exception as exc:
    
        import traceback
        print(traceback.format_exc())
        print("error", str(exc)) 

def save_telemetry(yr, rc, sn):
    
    file_name = f"{yr}_{rc}_{sn}_summary.csv"
    folder_name = f"{yr}_{rc}_{sn}"
    
    try:
        if check_if_folder_exists(folder_name):
            raise Exception("Folder already exists")
        
        if "test" in rc.lower() or "pre-season" in rc.lower():
            raise Exception("Test session")
        
        if rc == "Sprint Shootout":
            raise Exception("Sprint Shootout")

        session = get_sess(yr, rc, sn)
        session.load()
        laps = session.laps
        
        try:
            os.mkdir("record_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn))
        except:
            pass
        
        blue_flag_folder_id = get_folder_id(str(yr) + "_" + str(rc) + "_" + str(sn))     
        print(blue_flag_folder_id)
        if blue_flag_folder_id is None:
            blue_flag_folder_id = create_folder('Blue F1ag', str(yr) + "_" + str(rc) + "_" + str(sn))
            print(blue_flag_folder_id)
            
        drivers = laps['Driver'].unique()
        
        for driver in drivers:
            lap = 1
            while lap <= int(laps[laps['Driver'] == driver]['LapNumber'].max()) + 1:
                try:
                    driver_laps = session.laps.pick_driver(driver)
                    fast = driver_laps[driver_laps['LapNumber'] == int(lap)].iloc[0]
                    telemetry = fast.get_car_data().add_distance()
                    
                    csv_file_name = f"{yr}_{rc}_{sn}_{driver}_{lap}_telemetry.csv"
                    telemetry.to_csv("record_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + csv_file_name, index=False)
                    
                except:
                    pass
                lap += 1
        
        summary_data = []
        for driver in drivers:
            # find max numver of laps for driver and loop through
            for lap in range(1, int(laps[laps['Driver'] == driver]['LapNumber'].max()) + 1):
                summary_data.append({'driver': driver, 'lap': lap})
        summary_df = pd.DataFrame(summary_data)
        summary_file_name = f"{yr}_{rc}_{sn}_summary.csv"
        summary_df.to_csv("record_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + summary_file_name, index=False)
        
        for driver in drivers:
            max_lap = int(laps[laps['Driver'] == driver]['LapNumber'].max())
            for lap in range(1, max_lap + 1):
                try:
                    csv_file_name = f"{yr}_{rc}_{sn}_{driver}_{lap}_telemetry.csv"
                    upload_file_to_folder(str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + csv_file_name, blue_flag_folder_id)
                    print("Uploaded", csv_file_name)
                    delete_file(str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + csv_file_name)
                except:
                    pass
        
        upload_file_to_folder(str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + summary_file_name, blue_flag_folder_id)
        delete_file(str(yr) + "_" + str(rc) + "_" + str(sn) + "/" +summary_file_name)
        
        os.rmdir("record_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn))

    except Exception as exc:
        import traceback
        print(traceback.format_exc())
        print("Error:", str(exc))

def get_laps(yr, rc, sn):
    
    try:
    
        file_name = f"{yr}_{rc}_{sn}_laps.csv"
        download_file(get_file_id(file_name, "Blue F1ag"), file_name)
        # laps = read_record_from_file(file_name)
        laps = pd.read_csv("record_dump/" + file_name)
        delete_file(file_name)
        
        
        for col in laps.columns:
            if col.lower().__contains__("time"):
                laps[col] = pd.to_timedelta(laps[col])

        return laps
    
    except:
        
        return None

def get_telemetry(yr, rc, sn, driver, lap):
    
    try:
        
        file_name = f"{yr}_{rc}_{sn}_{driver}_{lap}_telemetry.csv"
        folder_name = f"{yr}_{rc}_{sn}"
        
        download_file(get_file_id(file_name, folder_name), file_name)
        # telemetry = read_record_from_file(file_name)
        
        telemetry = pd.read_csv("record_dump/" + file_name)
        
        delete_file(file_name)
        
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
                print(str(yr), str(rc), str(sn), "done")
                
            if flag == "telemetry":
                save_telemetry(yr, rc, sn)
                print(str(yr), str(rc), str(sn), "done")

def save_from(yr, flag):
    for yr in range(yr, dt.datetime.now().year + 1):
        save(yr, flag)
                                        
### END OF TEMP FUNCTIONS ###


#### FOR TESTING ###

import traceback

try:
    
    done = False
    while(not done):
        try:
            # save_from(2018, "laps")
            save_from(2018, "telemetry")
            done = True
        except:
            done = False
        
    # save_laps(2023, "Bahrain Grand Prix", "Qualifying")
    # print(get_laps(2023, "Bahrain Grand Prix", "Qualifying"))
    # save_telemetry(2023, "Bahrain Grand Prix", "Qualifying")
    # print(get_telemetry(2023, "Bahrain Grand Prix", "Qualifying", "VER", 1))
    
    ...
    
except Exception as exc:
    
    print(traceback.format_exc())

### END OF TESTING ###