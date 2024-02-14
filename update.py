import pandas as pd
import requests
import datetime as dt
import fastf1 as ff1
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import aws_api
from utils import *

load_dotenv()

connection_string = os.getenv("connection_string")
db_name = os.getenv("db_name")

client = MongoClient(connection_string)
db = client[db_name]



# enable cache
try:
    ff1.Cache.enable_cache("doc_cache")
except: 
    pass

# set yr to current year
yr = dt.datetime.now().year

# get driver standings
def get_drivers_standings():
    url = "https://ergast.com/api/f1/" + str(yr) + "/driverStandings.json"
    response = requests.get(url)
    data = response.json()
    drivers_standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']  # noqa: E501
    return drivers_standings

# gets the driver standings in text format
def drvr(driver_standings):
    st = ""
    for _, driver in enumerate(driver_standings):

        st = st + \
            f"{driver['position']}: {driver['Driver']['code']}, Points: {driver['points']}" + "\n"
    return st

# gets the driver standings and plots them
def driver_func(yr):
    
    from requests.packages.urllib3.exceptions import InsecureRequestWarning

    def ergast_retrieve(api_endpoint: str):
        url = f'https://ergast.com/api/f1/{api_endpoint}.json'
        
        try:
            # Disable SSL verification
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            
            response = requests.get(url, verify=False, timeout=300)  # Set the timeout duration to 10 seconds
            response.raise_for_status()  # Raise an exception for any HTTP errors
            return response.json()['MRData']
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    colors = ["#333333", "#444444", "#555555", "#666666", "#777777", "#888888", "#999999", "#AAAAAA", "#BBBBBB", "#CCCCCC"]
    color_counter = 0

    # Specify the number of rounds we want in our plot (in other words, specify the current round)
    rounds = 365

    # Initiate an empty dataframe to store our data
    all_championship_standings = pd.DataFrame()

    # We also want to store which driver drives for which team, which will help us later
    driver_team_mapping = {}
    driver_point_mapping = {}

    # Initate a loop through all the rounds
    for i in range(1, rounds + 1):
        try:
            # Make request to driverStandings endpoint for the current round
            race = ergast_retrieve(f'{yr}/{i}/driverStandings')
            
            # Get the standings from the result
            standings = race['StandingsTable']['StandingsLists'][0]['DriverStandings']
            
            # Initiate a dictionary to store the current rounds' standings in
            current_round = {'round': i}
            
            # Loop through all the drivers to collect their information
            for i in range(len(standings)):
                try:
                    driver = standings[i]['Driver']['code']
                except:
                    driver = " ".join(word[0].upper()+word[1:] for word in(standings[i]['Driver']['driverId'].replace("_", " ")).split(" "))
                position = standings[i]['position']
                points = standings[i]['points']
                
                # Store the drivers' position
                current_round[driver] = int(position)
                
                # Create mapping for driver-team to be used for the coloring of the lines
                driver_team_mapping[driver] = standings[i]['Constructors'][0]['name']

                driver_point_mapping[driver] = points

            # Append the current round to our fial dataframe
            all_championship_standings = all_championship_standings.append(current_round, ignore_index=True)
        except:
            break
        
    rounds = i
        
    # Set the round as the index of the dataframe
    all_championship_standings = all_championship_standings.set_index('round')

    # Melt data so it can be used as input for plot
    all_championship_standings_melted = pd.melt(all_championship_standings.reset_index(), ['round'])

    # Increase the size of the plot 
    sns.set(rc={'figure.figsize':(11.7,8.27)})
    if yr<2005:
        sns.set(rc={'figure.figsize':(13,8.27)})
        if yr<1996:
            sns.set(rc={'figure.figsize':(14,10)})

    # Initiate the plot
    fig, ax = plt.subplots()

    # Set the title of the plot
    ax.set_title(str(yr) + " Championship Standing", color = 'white')
    fig.set_facecolor("black")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")

    # Draw a line for every driver in the data by looping through all the standings
    # The reason we do it this way is so that we can specify the team color per driver
    for driver in pd.unique(all_championship_standings_melted['variable']):
        try:
            color=ff1.plotting.team_color(driver_team_mapping[driver])
        except:
            color=colors[color_counter]
        sns.lineplot(
            x='round', 
            y='value', 
            data=all_championship_standings_melted.loc[all_championship_standings_melted['variable']==driver], 
            color=color
        )
        try:
            color=ff1.plotting.team_color(driver_team_mapping[driver])
        except:
            color_counter += 1
            if color_counter >= len(colors):
                color_counter = 0

    # Invert Y-axis to have championship leader (#1) on top
    ax.invert_yaxis()

    # Set the values that appear on the x- and y-axes
    ax.set_xticks(range(1, rounds))
    if yr>1995:
        ax.set_yticks(range(1, len(driver_team_mapping)+1))
    else:
        ax.set_yticks(range(1, 31))

    # set colorbar tick color
    ax.yaxis.set_tick_params(color='white')
    ax.xaxis.set_tick_params(color='white')

    # set colorbar ticklabels
    plt.setp(plt.getp(ax.axes, 'yticklabels'), color='white')
    plt.setp(plt.getp(ax.axes, 'xticklabels'), color='white')
    ax.set_facecolor('black')

    ax.spines['bottom'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['right'].set_color('black')
    for t in ax.xaxis.get_ticklines(): t.set_color('black')
    for t in ax.yaxis.get_ticklines(): t.set_color('black')

    # Set the labels of the axes
    ax.set_xlabel("Round", color = 'white')
    ax.set_ylabel("Championship position", color = 'white')

    # Disable the gridlines 
    ax.grid(False)
    
    # Add the driver name to the lines
    for line, name , points in zip(ax.lines, all_championship_standings.columns.tolist(), driver_point_mapping.values()):
        y = line.get_ydata()[-1]
        x = line.get_xdata()[-1]
            
        text = ax.annotate(
            name + ": " + str(points),
            xy=(x + 0.1, y),
            xytext=(0, 0),
            color=line.get_color(),
            xycoords=(
                ax.get_xaxis_transform(),
                ax.get_yaxis_transform()
            ),
            textcoords="offset points"
        )

    # Save the plot
    #plt.show()
    file = str(yr) + "_DRIVERS_STANDINGS" + '.png'
    plt.savefig("data_dump/" + file)
    aws_api.upload_file("data_dump/" + file, file, "standings/")
    aws_api.delete_file_local(file)

# get constructorss standings
def get_constructors_standings():
    url = "https://ergast.com/api/f1/" + \
        str(yr) + "/constructorStandings.json"
    response = requests.get(url)
    data = response.json()
    constructors_standings = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']  # noqa: E501
    return constructors_standings

# get the constructors standings in text format
def constr(constructor_standings):
    st = ""
    for _, constructor in enumerate(constructor_standings):

        st = st + \
            f"{constructor['position']}: {constructor['Constructor']['name']}, Points: {constructor['points']}" + "\n"
    return st

# get the constructors standings and plots them
def const_func(yr):
    
    from requests.packages.urllib3.exceptions import InsecureRequestWarning

    def ergast_retrieve(api_endpoint: str):
        url = f'https://ergast.com/api/f1/{api_endpoint}.json'
        
        try:
            # Disable SSL verification
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            
            response = requests.get(url, verify=False, timeout=300)  # Set the timeout duration to 10 seconds
            response.raise_for_status()  # Raise an exception for any HTTP errors
            return response.json()['MRData']
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    colors = ["#333333", "#444444", "#555555", "#666666", "#777777", "#888888", "#999999", "#AAAAAA", "#BBBBBB", "#CCCCCC"]
    color_counter = 0

    # Specify the number of rounds we want in our plot (in other words, specify the current round)
    rounds = 365

    # Initiate an empty dataframe to store our data
    all_championship_standings = pd.DataFrame()

    # We also want to store which driver drives for which team, which will help us later
    constructor_team_mapping = {}
    constructor_point_mapping = {}

    # Initate a loop through all the rounds
    for i in range(1, rounds + 1):
        try:
            # Make request to driverStandings endpoint for the current round
            race = ergast_retrieve(f'{yr}/{i}/constructorStandings')
            
            # Get the standings from the result
            standings = race['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
            
            # Initiate a dictionary to store the current rounds' standings in
            current_round = {'round': i}
            
            # Loop through all the drivers to collect their information
            for i in range(len(standings)):
                constructor = standings[i]['Constructor']['name']
                position = standings[i]['position']
                points = standings[i]['points']
                
                # Store the drivers' position
                current_round[constructor] = int(position)
                
                # Create mapping for driver-team to be used for the coloring of the lines
                constructor_team_mapping[constructor] = standings[i]['Constructor']['name']
                
                constructor_point_mapping[constructor] = points


            # Append the current round to our fial dataframe
            all_championship_standings = all_championship_standings.append(current_round, ignore_index=True)
        except:
            break
        
    rounds = i
        
    # Set the round as the index of the dataframe
    all_championship_standings = all_championship_standings.set_index('round')

    # Melt data so it can be used as input for plot
    all_championship_standings_melted = pd.melt(all_championship_standings.reset_index(), ['round'])

    # Increase the size of the plot 
    sns.set(rc={'figure.figsize':(15,8.27)})
    if yr == 1961 or yr == 1962 or yr == 1971:
        sns.set(rc={'figure.figsize':(16,8.27)})

    # Initiate the plot
    fig, ax = plt.subplots()

    # Set the title of the plot
    ax.set_title(str(yr) + " Championship Standing", color = 'white')
    fig.set_facecolor("black")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")

    # Draw a line for every driver in the data by looping through all the standings
    # The reason we do it this way is so that we can specify the team color per driver
    for constructor in pd.unique(all_championship_standings_melted['variable']):
        try:
            color=ff1.plotting.team_color(constructor_team_mapping[constructor])
        except:
            color=colors[color_counter]
        sns.lineplot(
            x='round', 
            y='value', 
            data=all_championship_standings_melted.loc[all_championship_standings_melted['variable']==constructor], 
            color=color
        )
        try:
            color=ff1.plotting.team_color(constructor_team_mapping[constructor])
        except:
            color_counter += 1
            if color_counter >= len(colors):
                color_counter = 0

    # Invert Y-axis to have championship leader (#1) on top
    ax.invert_yaxis()

    # Set the values that appear on the x- and y-axes
    ax.set_xticks(range(1, rounds))
    ax.set_yticks(range(1, len(constructor_team_mapping)+1))

    # set colorbar tick color
    ax.yaxis.set_tick_params(color='white')
    ax.xaxis.set_tick_params(color='white')

    # set colorbar ticklabels
    plt.setp(plt.getp(ax.axes, 'yticklabels'), color='white')
    plt.setp(plt.getp(ax.axes, 'xticklabels'), color='white')
    ax.set_facecolor('black')

    ax.spines['bottom'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['right'].set_color('black')
    for t in ax.xaxis.get_ticklines(): t.set_color('black')
    for t in ax.yaxis.get_ticklines(): t.set_color('black')

    # Set the labels of the axes
    ax.set_xlabel("Round", color = 'white')
    ax.set_ylabel("Championship position", color = 'white')

    # Disable the gridlines 
    ax.grid(False)

    # Add the driver name to the lines
    for line, name, points in zip(ax.lines, all_championship_standings.columns.tolist(), constructor_point_mapping.values()):
        y = line.get_ydata()[-1]
        x = line.get_xdata()[-1]
            
        text = ax.annotate(
            name.replace("amp;", "") + ": " + str(points),
            xy=(x + 0.1, y),
            xytext=(0, 0),
            color=line.get_color(),
            xycoords=(
                ax.get_xaxis_transform(),
                ax.get_yaxis_transform()
            ),
            textcoords="offset points"
        )

    # Save the plot
    #plt.show()
    file = str(yr) + "_CONSTRUCTORS_STANDINGS" + '.png'
    plt.savefig("data_dump/" + file)
    aws_api.upload_file("data_dump/" + file, file, "standings/")
    aws_api.delete_file_local(file)

### updates standings for both drivers and constructors ###
def update(yr):
    
    stnd = False
    
    try:
        if yr >= 1950:
            driver_func(yr)              
            print("FINISHED UPDATE D")
        if yr >= 1958:
            const_func(yr)
            print("FINISHED UPDATE C")
        stnd = True

    except Exception as exc:
        
        print(str(exc) + "\nNO STANDINGS DATA FROM THIS YEAR")
        stnd = False
        
    return stnd

### updates standings for both drivers and constructors from a given year onwards ###
def update_from(i):
    while i >= 1950:
        try:
            update(i)
            print("FINISHED UPDATE " + str(i))
        except Exception as exc:
            print(str(exc) + "\nFAILED UPDATE " + str(i))
        i -= 1

### updates mongo with races of a given year ###
def update_races(yr):
    collection_name = "races"
    collection = db[collection_name]
    # if doc exists with yr not exists, create doc
    if collection.count_documents({"year": int(yr)}) == 0:
        schedule = ff1.get_event_schedule(yr)
        df = schedule[['EventName']]
        df = df.values
        df = df.tolist()
        races = []
        for i in df:
            races.append(i[0])
        collection.insert_one({"year": yr, 'races': races})

### updates mongo with data of all sessions of a given year and returns a list of all updated sessions ###
def update_data(yr):
    res = []
    msg = "Err"
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
            if sn == "Sprint Shootout":
                sn = "Sprint"
            collection_name = "data"
            collection = db[collection_name]
            if collection.count_documents({"year": int(yr), "race": rc, "session": sn}) > 0:
                pass
            elif "testing" in rc.lower():
                pass
            else:
                try:
                    print(yr, rc, sn)
                    try:
                        drivers = get_drivers(yr, rc, sn)
                    except Exception as exc:
                        print(str(exc) + "\nNO DRIVERS DATA")
                    try:
                        laps = get_laps(yr, rc, sn)
                    except Exception as exc:
                        print(str(exc) + "\nNO LAPS DATA")
                    try:
                        distance = get_distance(yr, rc, sn)
                    except Exception as exc:
                        print(str(exc) + "\nNO DISTANCE DATA")
                        distance = 0
                        if rc.lower().__contains__("austria"):
                            distance = 4300
                    collection.insert_one({
                        "year": int(yr),
                        "race": rc,
                        "session": sn,
                        "drivers": drivers,
                        "laps": laps,
                        "distance": distance
                    })
                    res.append([yr, rc, sn])
                except Exception as exc:
                    print(str(exc))
                    if res == []:
                        msg = "No sessions updated."
                        return msg
                    else:
                        msg = "Sessions updated:"
                        return msg + "\n" + str(res)

### updates gd with lap and telemetry data of all sessions of a given year ###       
def update_aws(yr):
    aws_api.save(yr, "laps")
    aws_api.save(yr, "telemetry")
   
# update(yr)

# update_from(yr)

# update_races(yr)

# print(update_data(yr))