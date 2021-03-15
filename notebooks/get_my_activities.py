import requests
import urllib3
import json
import os
from datetime import datetime
from pprint import pprint
import pandas as pd

# My notebooks for this proj
from functions import *
from secrets import *

# Set up parameters, API endpoints and allow requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
auth_url = "https://www.strava.com/oauth/token"
activities_url = "https://www.strava.com/api/v3/athlete/activities"

# Use function to get first of this and last month
before_dt, after_dt = get_strava_range()
date_str = str(after_dt.strftime("%B")) + str(after_dt.strftime("%Y"))
print('Date string for files: ', date_str)
email_str = str(after_dt.strftime("%b")) + ' ' + str(after_dt.strftime("%Y"))
print('Date string for email header: ', email_str)

# Filepaths used 
# NB: to get this working from the .bat file needed to include dir_path and '..' below
dir_path = os.path.dirname(os.path.realpath(__file__))
print('Current dir: ', dir_path)

activity_dir = "activity_data"
activity_path = os.path.join(dir_path, '..', activity_dir, f"{date_str}.json") 

success_dir = "status"
success_path = os.path.join(dir_path, '..', success_dir, f"{date_str}.txt")

# Check top folders exist and create if not 
try:
    os.mkdir(activity_dir)
except FileExistsError:
    pass
except PermissionError:
    pass

try:
    os.mkdir(success_dir)
except FileExistsError:
    pass
except PermissionError:
    pass

# Check if already run for this month
if os.path.exists(success_path):
    exit('Already sent email for ' + email_str + '..... Stopping run here')

# Ongoing payload that works with refresh
payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'refresh_token': refresh_token,
    'grant_type': "refresh_token",
    'f': 'json'
}

# Get access token
print('Getting new access token...')
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']

# Get activities
header = {'Authorization': 'Bearer ' + access_token}
before_dt, after_dt = get_strava_range()
print('Requesting Strava activity data between ', str(after_dt)[0:10], ' and ', str(before_dt)[0:10])
param = {'per_page': 50, 'page': 1, 'before': before_dt.timestamp(), 'after':after_dt.timestamp()}
all_data = requests.get(activities_url, headers=header, params=param).json() # returns a list of dicts 
print('Collected activities: ', str(len(all_data)))

# Get just the info we want from each activity
relevant_keys = ["id", "distance", "moving_time", "total_elevation_gain", "type", "start_date_local", "average_speed", "max_speed"]
relevant_data = [{rel_key : activity[rel_key] for rel_key in relevant_keys} for activity in all_data] 

# Save relevant data out
with open(activity_path, 'w+') as outfile:
    json.dump(relevant_data, outfile)
print('Saved activity data to: ', activity_path)
print('-'*30)

# activity is list of dicts so can convert straight to dataframe
activity_pd = pd.DataFrame(relevant_data)
activity_pd['Activities'] = 1
agg_activity_pd = activity_pd.groupby("type").sum().reset_index()
agg_activity_pd['Moving hrs'] = round(agg_activity_pd['moving_time']/(60*60), 1)
agg_activity_pd['Distance (km)'] = round(agg_activity_pd['distance']/1000, 1)
agg_activity_pd = agg_activity_pd.rename(columns={'total_elevation_gain': 'Elevation gain (m)', 'type': 'Type'})
final_cols = ['Type','Activities', 'Moving hrs', 'Distance (km)', 'Elevation gain (m)']
final_pd = agg_activity_pd[final_cols]
print(email_str + ' Summary data:')
print(final_pd)
print('-'*30)

# Covert aggregated table to html for email 
monthly_data = final_pd.to_html()

try:
    send_email(receiver_address, email_str, monthly_data)
except Exception as e:
    print('Couldn\'t send email: ', e)
    raise

# Write out a file to confirm successful run (use to check if this has run for each month already)
with open(success_path, 'w+') as file:
         file.write('Smashed it for ' + email_str)
print('Success file written to: ', success_path)
