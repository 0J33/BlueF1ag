import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import fastf1 as ff1
import aws_api

#quali battles
def battles_func(yr):

    def ergast_retrieve(api_endpoint: str):
        url = f'https://ergast.com/api/f1/{api_endpoint}.json'
        response = requests.get(url).json()
        
        return response['MRData']

    # By changing these params you can easily get other seasons 
    
    colors = ["#333333", "#444444", "#555555", "#666666", "#777777", "#888888", "#999999", "#AAAAAA", "#BBBBBB", "#CCCCCC"]
    color_counter = 0
    
    drivers_to_exclude = []

    if yr == 2024:
        drivers_to_exclude = []
    if yr == 2023:
        drivers_to_exclude = ['DEV', 'LAW']
    elif yr == 2022:
        drivers_to_exclude = ['HUL', 'DEV']
    elif yr == 2021:
        drivers_to_exclude = ['KUB']
    elif yr == 2020:
        drivers_to_exclude = ['HUL', 'AIT', 'FIT']
    elif yr == 2019:
        drivers_to_exclude = ['GAS', 'ALB']
    elif yr == 2018:
        drivers_to_exclude = []
    elif yr == 2017:
        drivers_to_exclude = ['BUT', 'GIO', 'DIR', 'PAL', 'GAS', 'HAR', 'KVY']
    elif yr == 2016:
        drivers_to_exclude = ['VAN', 'VER', 'KVY', 'HAR', 'OCO']
    elif yr == 2015:
        drivers_to_exclude = ['MER', 'RSS']
    elif yr == 2014:
        drivers_to_exclude = []
    elif yr == 2013:
        drivers_to_exclude = ['KOV']
    elif yr == 2012:
        drivers_to_exclude = ['GRO', 'JER', 'DAM', 'AMB']
    elif yr == 2011:
        drivers_to_exclude = ['DLR', 'KAR', 'RIC', 'CHA', 'TRU', 'SEN', 'HEI', 'KAR', 'PER', 'LIU']
    elif yr == 2010:
        drivers_to_exclude = ['YAM', 'CHA', 'KLI', 'HEI', 'DLR']
    elif yr == 2009:
        drivers_to_exclude = ['GLO', 'MAS', 'KOB', 'BOU', 'PIQ', 'LIU', 'GRO', 'ALG', 'BAD']
    elif yr == 2008:
        drivers_to_exclude = ['SAT', 'DAB']
    elif yr == 2007:
        drivers_to_exclude = ['KUB', 'WUR', 'VET', 'SPE', 'NAK', 'YAM', 'ALB', 'WIN']
    elif yr == 2006:
        drivers_to_exclude = ['MOY', 'DLR', 'VIL', 'KUB', 'DOO', 'IDE', 'YAM', 'MON']
    elif yr == 2005:
        drivers_to_exclude = ['MOY', 'KLI', 'WUR', 'DLR', 'FRI', 'PIZ', 'SAT', 'LIU', 'DOO', 'DAV', 'ZON']
    elif yr == 2004:
        drivers_to_exclude = []
    elif yr == 2003:
        drivers_to_exclude = []
    elif yr == 2002:
        drivers_to_exclude = []
    elif yr == 2001:
        drivers_to_exclude = []
    elif yr == 2000:
        drivers_to_exclude = []
    elif yr == 1999:
        drivers_to_exclude = []
    elif yr == 1998:
        drivers_to_exclude = []
    elif yr == 1997:
        drivers_to_exclude = []
    elif yr == 1996:
        drivers_to_exclude = []
    elif yr == 1995:
        drivers_to_exclude = []
    elif yr == 1994:
        drivers_to_exclude = []
    elif yr == 1993:
        drivers_to_exclude = []
    elif yr == 1992:
        drivers_to_exclude = []
    elif yr == 1991:
        drivers_to_exclude = []
    elif yr == 1990:
        drivers_to_exclude = []
    elif yr == 1989:
        drivers_to_exclude = []
    elif yr == 1988:
        drivers_to_exclude = []
    elif yr == 1987:
        drivers_to_exclude = []
    elif yr == 1986:
        drivers_to_exclude = []
    elif yr == 1985:
        drivers_to_exclude = []
    elif yr == 1984:
        drivers_to_exclude = []
    elif yr == 1983:
        drivers_to_exclude = []
    elif yr == 1982:
        drivers_to_exclude = []
    elif yr == 1981:
        drivers_to_exclude = []
    elif yr == 1980:
        drivers_to_exclude = []
    elif yr == 1979:
        drivers_to_exclude = []
    elif yr == 1978:
        drivers_to_exclude = []
    elif yr == 1977:
        drivers_to_exclude = []
    elif yr == 1976:
        drivers_to_exclude = []
    elif yr == 1975:
        drivers_to_exclude = []
    elif yr == 1974:
        drivers_to_exclude = []
    elif yr == 1973:
        drivers_to_exclude = []
    elif yr == 1972:
        drivers_to_exclude = []
    elif yr == 1971:
        drivers_to_exclude = []
    elif yr == 1970:
        drivers_to_exclude = []
    elif yr == 1969:
        drivers_to_exclude = []
    elif yr == 1968:
        drivers_to_exclude = []
    elif yr == 1967:
        drivers_to_exclude = []
    elif yr == 1966:
        drivers_to_exclude = []
    elif yr == 1965:
        drivers_to_exclude = []
    elif yr == 1964:
        drivers_to_exclude = []
    elif yr == 1963:
        drivers_to_exclude = []
    elif yr == 1962:
        drivers_to_exclude = []
    elif yr == 1961:
        drivers_to_exclude = []
    elif yr == 1960:
        drivers_to_exclude = []
    elif yr == 1959:
        drivers_to_exclude = []
    elif yr == 1958:
        drivers_to_exclude = []
    elif yr == 1957:
        drivers_to_exclude = []
    elif yr == 1956:
        drivers_to_exclude = []
    elif yr == 1955:
        drivers_to_exclude = []
    elif yr == 1954:
        drivers_to_exclude = []
    elif yr == 1953:
        drivers_to_exclude = []
    elif yr == 1952:
        drivers_to_exclude = []
    elif yr == 1951:
        drivers_to_exclude = []
    elif yr == 1950:
        drivers_to_exclude = []

    all_quali_results = pd.DataFrame()

    # We want this so that we know which driver belongs to which team, so we can color them later
    team_drivers = {}

    current_round = 1

    while True:
        race = ergast_retrieve(f'{yr}/{current_round}/qualifying')
        
        # If session doesn't exist, cancel loop
        if not race['RaceTable']['Races']:
            break

        results = race['RaceTable']['Races'][0]['QualifyingResults']

        quali_results = {'round': current_round}

        for j in range(len(results)):
            try:
                driver = results[j]['Driver']['code']
            except:
                driver = " ".join(word[0].upper()+word[1:] for word in(results[j]['Driver']['driverId'].replace("_", "\n")).split(" "))
            position = int(results[j]['position'])
            team = results[j]['Constructor']['name']
            
            if driver in drivers_to_exclude:
                continue
            
            # Create mapping for driver - team
            if not team in team_drivers:
                team_drivers[team] = [driver]
            else:
                if not driver in team_drivers[team]:
                    team_drivers[team].append(driver)
                    
            quali_results[driver] = position
                
        all_quali_results = all_quali_results.append(quali_results, ignore_index=True)
        
        current_round += 1
        
    # Now we want to know, per round, per team, who qualified higher?
    all_quali_battle_results = []
    team_colors_palette = []

    for team in team_drivers:
        drivers = team_drivers[team]
        
        quali_results = all_quali_results[drivers]
        
        # We do dropna() to only include the sessions in which both drivers participated
        fastest_driver_per_round = quali_results.dropna().idxmin(axis=1)
        
        quali_battle_result = fastest_driver_per_round.value_counts().reset_index()
        
        for _, driver in quali_battle_result.iterrows():
            all_quali_battle_results.append({
                'driver': driver['index'],
                'team': team,
                'quali_score': driver[0]
            })
        try:
            team_colors_palette.append(ff1.plotting.team_color(team))
        except:
            team_colors_palette.append(colors[color_counter])
            color_counter += 1
            if color_counter >= len(colors):
                color_counter = 0
        # If none, replace None with grey
        team_colors_palette = ['#D3D3D3' if v is None else v for v in team_colors_palette]


    # Finally, convert to a DataFrame so we can plot
    all_quali_battle_results = pd.DataFrame.from_dict(all_quali_battle_results)

    # Increase the size of the plot 
    sns.set(rc={'figure.figsize':(11.7,8.27)})

    # Create custom color palette
    custom_palette = sns.set_palette(sns.color_palette(team_colors_palette))

    fig, ax = plt.subplots()

    ax.set_title(f"{yr} Teammate Qualifying Battle", color = 'white')
    fig.set_facecolor("black")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
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
    ax.set_facecolor('black')

    g = sns.barplot(
        x='driver',
        y='quali_score', 
        hue='team',
        data=all_quali_battle_results, 
        dodge=False,
        palette=custom_palette,
    )

    plt.yticks(range(max(all_quali_battle_results['quali_score']) + 1))

    plt.legend([],[], frameon=False)

    g.set(xlabel=None)
    g.set(ylabel=None)
    
    file = str(yr) + "_QUALI" + '.png'
    plt.savefig("data_dump/" + file)
    aws_api.upload_file("data_dump/" + file, file, "battles/")
    aws_api.delete_file_local(file)