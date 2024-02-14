import boto3
import os
from dotenv import load_dotenv
import datetime as dt
import pandas as pd
from pymongo import MongoClient
from utils import *
import traceback

load_dotenv()

connection_string = os.getenv("connection_string")
db_name = os.getenv("db_name")

client = MongoClient(connection_string)
db = client[db_name]

bucket_name = os.getenv("bucket_name")
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
aws_region = os.getenv("aws_region")

# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

### NOTES ###

# bucket_name = 'your_bucket_name'
# local_file_path = 'path/to/your/local/file.txt'
# s3_nested_folders = 'your/s3/nested/folders/'
# folder_path = 'your/s3/folder/'

### END OF NOTES ###

### AWS API FUNCTIONS ###
    
def upload_file(local_file_path, file_name, s3_nested_folders):
    try:
        # s3.put_object(Bucket=bucket_name, Key=s3_nested_folders)
        s3.upload_file(local_file_path, bucket_name, s3_nested_folders + file_name)
        print(f'The file has been uploaded to {bucket_name}/{s3_nested_folders}{file_name}')
        return True
    except Exception as e:
        print(f'An error occurred: {e}')
        return False
    
def create_folder(folder_path):
    try:
        s3.put_object(Bucket=bucket_name, Key=folder_path)
        print(f'The folder {bucket_name}/{folder_path} has been created.')
        return True
    except Exception as e:
        print(f'An error occurred: {e}')
        return False
    
def check_folder_exists(folder_path):
    try:
        s3.head_object(Bucket=bucket_name, Key=folder_path)
        print(f'The folder {bucket_name}/{folder_path} exists.')
        return True
    except Exception as e:
        if e.response['Error']['Code'] == '404':
            print(f'The folder {bucket_name}/{folder_path} does not exist.')
            return False
        else:
            print(f'An error occurred: {e}')
            return e
            
def check_file_exists(file_path):
    try:
        s3.head_object(Bucket=bucket_name, Key=file_path)
        print(f'The file {bucket_name}/{file_path} exists.')
        return True
    except Exception as e:
        if e.response['Error']['Code'] == '404':
            print(f'The file {bucket_name}/{file_path} does not exist.')
            return False
        else:
            print(f'An error occurred: {e}')
            return e
            
def read_file(file_path):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_path)
        file_content = response['Body'].read().decode('utf-8')
        return file_content
    except Exception as e:
        print(f'An error occurred: {e}')
        return e
    
def delete_file(file_path):
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_path)
        print(f'The file {bucket_name}/{file_path} has been deleted.')
        return True
    except Exception as e:
        print(f'An error occurred: {e}')
        return False
    
def delete_folder(folder_path):
    try:
        s3.delete_object(Bucket=bucket_name, Key=folder_path)
        print(f'The folder {bucket_name}/{folder_path} has been deleted.')
        return True
    except Exception as e:
        print(f'An error occurred: {e}')
        return False

def save_data_as_file(data, file_name):
    with open("data_dump/" + file_name, 'w') as f:
        for i in data:
            for j in i:
                f.write(str(j) + ",")
            f.write("\n")
        
def read_data_from_file(file_name):
    with open("data_dump/" + file_name, 'r') as f:
        data = f.read()
    return data

def delete_file_local(file_name):
    os.remove("data_dump/" + file_name)
    
###

def save_laps(yr, rc, sn):
    
    file_name = f"{yr}_{rc}_{sn}_laps.csv"
    
    try:
        
        if check_file_exists(f"laps/{file_name}"):
            raise Exception("File already exists")
        
        if "test" in rc.lower() or "pre-season" in rc.lower():
            raise Exception("Test session")
        
        if rc == "Sprint Shootout":
            raise Exception("Sprint Shootout")
        
        if not check_folder_exists(f"laps/{file_name}"):
            
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
            
            save_data_as_file(new_laps, file_name)
            upload_file("data_dump/" + file_name, file_name, "laps/")
            delete_file_local(file_name)
            
    except Exception as exc:
    
        print(traceback.format_exc())
        print("error", str(exc)) 
        
def save_telemetry(yr, rc, sn):
    
    file_name = f"{yr}_{rc}_{sn}_summary.csv"
    folder_name = f"{yr}_{rc}_{sn}"
        
    try:
        
        if check_folder_exists(f"telemetry/{folder_name}"):
            raise Exception("Folder already exists")
        
        if "test" in rc.lower() or "pre-season" in rc.lower():
            raise Exception("Test session")
        
        if rc == "Sprint Shootout":
            raise Exception("Sprint Shootout")

        session = get_sess(yr, rc, sn)
        session.load()
        laps = session.laps
        
        try:
            os.mkdir("data_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn))
        except:
            pass
        
         
        drivers = laps['Driver'].unique()
        
        for driver in drivers:
            lap = 1
            while lap <= int(laps[laps['Driver'] == driver]['LapNumber'].max()) + 1:
                try:
                    driver_laps = session.laps.pick_driver(driver)
                    fast = driver_laps[driver_laps['LapNumber'] == int(lap)].iloc[0]
                    telemetry = fast.get_car_data().add_distance()
                    
                    csv_file_name = f"{yr}_{rc}_{sn}_{driver}_{lap}_telemetry.csv"
                    telemetry.to_csv("data_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + csv_file_name, index=False)
                    
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
        summary_df.to_csv("data_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + summary_file_name, index=False)
        
        for driver in drivers:
            max_lap = int(laps[laps['Driver'] == driver]['LapNumber'].max())
            for lap in range(1, max_lap + 1):
                try:
                    csv_file_name = f"{yr}_{rc}_{sn}_{driver}_{lap}_telemetry.csv"
                    upload_file("data_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + csv_file_name, csv_file_name, f"telemetry/{folder_name}/")
                    print("Uploaded", csv_file_name)
                except:
                    pass
        
        upload_file("data_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + summary_file_name, summary_file_name, f"telemetry/{folder_name}/")
        for file in os.listdir("data_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn)):
            delete_file_local(str(yr) + "_" + str(rc) + "_" + str(sn) + "/" + file)
        os.rmdir("data_dump/" + str(yr) + "_" + str(rc) + "_" + str(sn))

    except Exception as exc:
        import traceback
        print(traceback.format_exc())
        print("Error:", str(exc))
        
def get_laps(yr, rc, sn):
    
    try:
    
        file_name = f"{yr}_{rc}_{sn}_laps.csv"
        laps = read_file("laps/" + file_name)
                
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
        
        telemetry = read_file("telemetry/" + folder_name + "/" + file_name)
        
        for col in telemetry.columns:
            if col.lower().__contains__("time"):
                telemetry[col] = pd.to_timedelta(telemetry[col])

        return telemetry
    
    except:
        
        return None

### END OF AWS API FUNCTIONS ###

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

try:
    
    done = False
    while(not done):
        try:
            # save_from(2018, "laps")
            # save_from(2018, "telemetry")
            done = True
        except:
            done = False

except Exception as exc:
    
    print(traceback.format_exc())

### END OF TESTING ###