import pathlib
import pandas as pd
import numpy as np
import random
import requests
import datetime
import fastf1 as ff1
from fastf1 import plotting
import seaborn as sns
import matplotlib.pyplot as plt
import platform
from PIL import Image, ImageDraw, ImageFont
from env import *
from git_func import *
platform.system()



dir_path = r"" + str(pathlib.Path(__file__).parent.resolve())

def get_path():
    if platform.system().__contains__("Win"):
        path = "\\"
    elif platform.system().__contains__("Lin"):
        path = "/"
    return path

yr = datetime.datetime.now().year



#helper
def get_drivers_standings():
    url = "https://ergast.com/api/f1/" + str(yr) + "/driverStandings.json"
    response = requests.get(url)
    data = response.json()
    drivers_standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']  # noqa: E501
    return drivers_standings

#text
def drvr(driver_standings):
    st = ""
    for _, driver in enumerate(driver_standings):

        st = st + \
            f"{driver['position']}: {driver['Driver']['code']}, Points: {driver['points']}" + "\n"
    return st

#main
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
    plt.savefig(dir_path + "\\res\\stnd\\" + str(yr) + "_DRIVERS_STANDINGS" + '.png')



#helper
def get_constructors_standings():
    url = "https://ergast.com/api/f1/" + \
        str(yr) + "/constructorStandings.json"
    response = requests.get(url)
    data = response.json()
    constructors_standings = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']  # noqa: E501
    return constructors_standings

#text
def constr(constructor_standings):
    st = ""
    for _, constructor in enumerate(constructor_standings):

        st = st + \
            f"{constructor['position']}: {constructor['Constructor']['name']}, Points: {constructor['points']}" + "\n"
    return st

#main
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
    plt.savefig(dir_path + "\\res\\stnd\\" + str(yr) + "_CONSTRUCTORS_STANDINGS" + '.png')



#update year
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

#update from year
def update_from(i):
    while i >= 1950:
        try:
            update(i)
            print("FINISHED UPDATE " + str(i))
        except Exception as exc:
            print(str(exc) + "\nFAILED UPDATE " + str(i))
        i -= 1



import csv
import datetime
import fastf1
import numpy as np

try:
    fastf1.Cache.enable_cache("doc_cache")
except: 
    pass

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

def get_sessions(yr, rc):
    yr = int(yr)
    sessions = []
    i=1
    while True:
        sess = 'Session' + str(i)
        fastf1_obj = fastf1.get_event(yr, rc)
        try: 
            sessions.append((getattr(fastf1_obj, sess)))
        except:
            break
        i+=1
    return sessions
 
def get_drivers(yr, rc, sn):
    session = fastf1.get_session(yr, rc, sn)
    session.load()
    laps = session.laps
    ls = set(tuple(x) for x in laps[['Driver']].values.tolist())
    lis = [x[0] for x in ls]
    return lis

def get_laps(yr, rc, sn):
    session = fastf1.get_session(yr, rc, sn)
    session.load()
    laps = session.laps
    ls = set(tuple(x) for x in laps[['LapNumber']].values.tolist())
    lis = sorted([int(x[0]) for x in ls])
    max = int(np.max(lis))
    return max

def get_distance(yr, rc, sn):
    session = fastf1.get_session(yr, rc, sn)
    session.load()
    laps = session.load_laps(with_telemetry=True)
    car_data = laps.pick_fastest().get_car_data().add_distance()
    maxdist = int(np.max(car_data['Distance']))
    return maxdist

def update_races():
    for yr in range(1950, datetime.datetime.now().year+1):
        if str(yr) not in open("res/races.txt").read():
            schedule = fastf1.get_event_schedule(yr)
            df = schedule[['EventName']]
            df = df.values
            df = df.tolist()
            df = str(df).replace("[","").replace("]","").replace("'","")
            content = (str(yr) + ":" + df + "\n")
            old = read_gist(GH_GIST_ID_RACES, "races")
            update_gist(old + content, GH_GIST_ID_RACES, "races")
            
def update_data():
    res = []
    msg = "Err"
    yr = datetime.datetime.now().year
    races_list = []
    races = read_gist(GH_GIST_ID_RACES, "races")
    old = read_gist(GH_GIST_ID_DATA, "data")
    data = races.split("\n")
    for i in range(1, len(data)):
        if str(yr) in data[i]:
            races_list = data[i][5:].split(",")
            break
    for rc in races_list:
        rc = rc.strip()
        sessions = get_sessions(yr, rc)
        for sn in sessions:
            print("Year:" + str(yr) + "," + "Race:" + str(rc) + "," + 'Session:' + str(sn))
            if old.__contains__("Year:" + str(yr) + "," + "Race:" + str(rc) + "," + 'Session:' + str(sn)):
                pass
            elif "testing" in rc.lower():
                pass
            elif "emilia romagna" in rc.lower():
                rc = "Emilia Romagna"
            else:
                try:
                    drivers = get_drivers(yr, rc, sn)
                    laps = get_laps(yr, rc, sn)
                    distance = get_distance(yr, rc, sn)
                    content = ("Year:" + str(yr) + "," + "Race:" + str(rc) + "," + "Session:" + str(sn) + "," + "Drivers:" + str(drivers).replace(",","/") + "," + "Laps:" + str(laps) + "," + "Distance:" + str(distance) + "\n")
                    update_gist((read_gist(GH_GIST_ID_DATA, "data")) + content, GH_GIST_ID_DATA, "data")
                    res.append(content)
                except:
                    if res == []:
                        msg = "No sessions updated."
                    else:
                        msg = "Sessions updated:"
                    return msg + "\n" + str(res)
                     
# update(yr)

# update_from(yr)

# update_races()

print(update_data())