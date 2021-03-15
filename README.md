# strava-summary 
Email self a summary of monthly Strava activity.

Mostly to play around with the Strava API and email formatting


# Usage
Clone locally. <br>
Followed this [awesome article](https://jessicasalbert.medium.com/holding-your-hand-through-stravas-api-e642d15695f2) to set up own application and set up to get refresh token with read_all scope <br>

Create a file secrets.py as a copy of secrets_template.py and substitute the following:
- client_id - int: from My API application
- client_secret - string: from My API application
- refresh_token - string: follow the linked blog to get this token, requires authorizing your account then making an additional post request
- sender_address - string: email address to send the summary from, I created a developer gmail account just to test this out 
- sender_pword - string: password for the above account
- receiver_address - string: email to send the results to


## Scheduling on Windows:
- Create a file run-strava.bat containing:
```
"<path to python>\python.exe" "<path to root of repo>\notebooks\get_my_activities.py" pause
```
- use Task Scheduler to set run-strava.bat to run on the first of every month at e.g. 8am