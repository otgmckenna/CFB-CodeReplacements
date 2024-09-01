import cfbd
import pandas as pd
from pprint import pprint
from datetime import datetime

currentYear = datetime.now().year

homeTeam = input("Enter the home team: ")   # Get the home team - Ex. Washington State
homeCoach = input("Enter the home coach: ") # Get the home coach - Ex. Jake Dickert
awayTeam = input("Enter the away team: ")   # Get the away team - Ex. Washington
awayCoach = input("Enter the away coach: ") # Get the away coach - Ex. Jedd Fisch

# Configure Bearer authorization: apiKey
configuration = cfbd.Configuration(
    access_token = 'API KEY HERE'    # Get your API key from here: https://collegefootballdata.com/
)

# Get the home team's roster
with cfbd.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    home_api_instance = cfbd.TeamsApi(api_client)
    team = homeTeam
    year = currentYear

    try:
        home_api_response = home_api_instance.get_roster(team=team, year=year)
        # print("The response of TeamsApi->get_roster:\n")
        # pprint(home_api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->get_roster: %s\n" % e)

# Get the away team's roster
with cfbd.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    away_api_instance = cfbd.TeamsApi(api_client)
    team = awayTeam
    year = currentYear

    try:
        away_api_response = away_api_instance.get_roster(team=team, year=year)
        # print("The response of TeamsApi->get_roster:\n")
        # pprint(away_api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->get_roster: %s\n" % e)

# Get each team's mascots
with cfbd.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    teams_api_instance = cfbd.TeamsApi(api_client)
    year = currentYear # int | Optional year filter to get historical conference affiliations (optional)

    try:
        teams_api_response = teams_api_instance.get_teams(year=year)
        # print("The response of TeamsApi->get_teams:\n")
        # pprint(teams_api_response)
    except Exception as e:
        print("Exception when calling TeamsApi->get_teams: %s\n" % e)

teams_list = []
for team in teams_api_response:
    teams_list.append(team.to_dict())
teams_df = pd.DataFrame(teams_list)

home_abbr = teams_df[teams_df['school'] == homeTeam]['abbreviation'].values[0]
away_abbr = teams_df[teams_df['school'] == awayTeam]['abbreviation'].values[0]

home_team_mascot = teams_df[teams_df['school'] == homeTeam]['mascot'].values[0]
away_team_mascot = teams_df[teams_df['school'] == awayTeam]['mascot'].values[0]

# Converting the API response to a list
home_roster = []
for player in home_api_response:
    home_roster.append(player.to_dict())
away_roster = []
for player in away_api_response:
    away_roster.append(player.to_dict())
    
# Converting the list to a DataFrame
home_df = pd.DataFrame(home_roster)
away_df = pd.DataFrame(away_roster)

# Dropping the columns that are not needed
home_df = home_df.drop(columns=['id', 'height', 'weight', 'year', 'homeCity', 'homeState', 'homeCountry', 'homeLatitude', 'homeLongitude', 'homeCountyFIPS', 'recruitIds'])
away_df = away_df.drop(columns=['id', 'height', 'weight', 'year', 'homeCity', 'homeState', 'homeCountry', 'homeLatitude', 'homeLongitude', 'homeCountyFIPS', 'recruitIds'])

positionFull = {
    'C': 'center',
    'CB': 'cornerback',
    'DB': 'defensive back',
    'DE': 'defensive end',
    'DL': 'defensive lineman',
    'DT': 'defensive tackle',
    'EDGE': 'edge rusher',
    'FB': 'fullback',
    'FS': 'free safety',
    'G': 'guard',
    'HB': 'halfback',
    'ILB': 'inside linebacker',
    'K': 'kicker',
    'LB': 'linebacker',
    'LS': 'long snapper',
    'MLB': 'middle linebacker',
    'NT': 'nose tackle',
    'NB': 'nickelback',
    'OG': 'offensive guard',
    'OL': 'offensive lineman',
    'OT': 'offensive tackle',
    'P': 'punter',
    'PK': 'kicker/punter',
    'QB': 'quarterback',
    'RB': 'running back',
    'S': 'safety',
    'SS': 'strong safety',
    'TE': 'tight end',
    'WR': 'wide receiver'
}

# Replacing the abbreviations with the full position names
home_df['position'] = home_df['position'].map(positionFull)
away_df['position'] = away_df['position'].map(positionFull)

# Combining the first and last names
home_df['name'] = home_df['firstName'] + ' ' + home_df['lastName']
away_df['name'] = away_df['firstName'] + ' ' + away_df['lastName']

# Dropping the first and last names
home_df = home_df.drop(columns=['firstName', 'lastName'])
away_df = away_df.drop(columns=['firstName', 'lastName'])

# Adding the mascots to the DataFrames
home_df['mascot'] = home_team_mascot
away_df['mascot'] = away_team_mascot

# Dropping null values in the Jersey column
home_df = home_df.dropna(subset=['jersey'])
away_df = away_df.dropna(subset=['jersey'])

# Converting the Jersey column to an integer
home_df['jersey'] = home_df['jersey'].astype(int)
away_df['jersey'] = away_df['jersey'].astype(int)

# Sorting the DataFrames by the Jersey column
home_df = home_df.sort_values(by='jersey')
away_df = away_df.sort_values(by='jersey')

# Resetting the index
home_df = home_df.reset_index(drop=True)
away_df = away_df.reset_index(drop=True)

# Add a new column to the DataFrames that indicated whether a player is on defense
defensePositions = ['cornerback', 'defensive back', 'defensive end', 'defensive lineman', 'Defensive tackle', 'edge rusher', 'free safety', 'linebacker', 'middle linebacker', 'nose tackle', 'nickelback', 'safety', 'strong safety']

home_df['defense'] = home_df['position'].isin(defensePositions)
away_df['defense'] = away_df['position'].isin(defensePositions)

# If True, replace with 'd', else replace with ''
home_df['defense'] = home_df['defense'].replace({True: 'd', False: ''})
away_df['defense'] = away_df['defense'].replace({True: 'd', False: ''})

# Generating a text file with the rosters for each team
# Format: abbr(jersey) \t team mascot position name (jersey)
homeSTR = home_abbr.lower() + home_df['jersey'].astype(str) + home_df['defense'] + '\t' + home_df['team'] + ' ' + home_team_mascot + ' ' + home_df['position'] + ' ' + home_df['name'] + ' (' + home_df['jersey'].astype(str) + ')'
awaySTR = away_abbr.lower() + away_df['jersey'].astype(str) + home_df['defense'] + '\t' + away_df['team'] + ' ' + away_team_mascot + ' ' + away_df['position'] + ' ' + away_df['name'] + ' (' + away_df['jersey'].astype(str) + ')'

homeCoachSTR = home_abbr.lower() + 'hc' + '\t' + homeTeam + ' ' + home_team_mascot + ' head coach ' + homeCoach
awayCoachSTR = away_abbr.lower() + 'hc' + '\t' + awayTeam + ' ' + away_team_mascot + ' head coach ' + awayCoach

# Write all strings to a text file
with open(f'{home_abbr}_{away_abbr}.txt', 'w') as file:
    file.write(homeCoachSTR)
    file.write('\n')
    file.write(homeSTR.str.cat(sep='\n'))
    file.write('\n')
    file.write(awayCoachSTR)
    file.write('\n')
    file.write(awaySTR.str.cat(sep='\n'))
