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

token = "YOUR_ACCESS_TOKEN"

headers = {
    "Authorization": f"Bearer {token}",
}


### ONE DRIVE API FUNCTIONS ###

# Delete folder
def delete_folder(folder_name):
    ...
    
# Check if folder exists
def check_if_folder_exists(folder_name):
    ...
    
# Check if file exists in folder
def check_file_in_folder(file_name, folder_name):
    ...
    
# Upload csv file to a specific folder
def upload_file_to_folder(full_name, folder_id):
    ...

# Get the ID of the "Blue F1ag" folder
def get_folder_id(folder_name):
    ...
    
# Get folder name using ID
def get_folder_name(folder_id):
    ...
    
# Download csv file
def download_file(file_id, file_name):
    ...
    
# Save data as file
def save_data_as_file(csv, file_name):
    ...
    
# Read data from file
def read_data_from_file(file_name):
    ...
    
# Get file ID
def get_file_id(file_name, folder_name):
    ...
    
# Delete file locally
def delete_file(file_name):
    ...
    
# Delete file from Google Drive
def delete_file_from_drive(file_id):
    ...
    
# Create folder
def create_folder(parent_folder_name, subfolder_name):
    ...
    
###

def save_laps(yr, rc, sn):
    ...
    
def save_telemetry(yr, rc, sn):
    ...
    
def get_laps(yr, rc, sn):
    ...
    
def get_telemetry(yr, rc, sn, driver, lap):
    ...
    
### END OF ONE DRIVE API FUNCTIONS ###


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
            save_from(2022, "telemetry")
            done = True
        except:
            done = False

except Exception as exc:
    
    print(traceback.format_exc())

### END OF TESTING ###