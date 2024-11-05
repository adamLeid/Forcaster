#General Imports
import requests
from datetime import date
from datetime import datetime
import calendar
import json
from DayForcast import DayForcast
from FullDayForcast import FullDayForcast

#Gmail API imports
import base64
from email.message import EmailMessage
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

#NWS API
rnk_url_forcast_12hr = "https://api.weather.gov/gridpoints/RNK/21,36/forecast" #12 hour forcast endpoint. Update as needed
rnk_url_forcast_hourly = "https://api.weather.gov/gridpoints/RNK/21,36/forecast/hourly" #hourly forcast enpoint. Update as needed
rnk_url_forcast = "https://api.weather.gov/gridpoints/RNK/21,36" #high level forcast endpoint. Update as needed

currentDate = date.today()
emailList =""#Fill in email list here, seperated with ;
sender = "Weather Forcaster <@gmail.com>" #fill in sender email to use for the alerts
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Get the seven day forcast. Default is 12hr if type is empty
def getNationalWeatherServiceAPI(type):
    if (type == "hourly"):
        return requests.get(rnk_url_forcast_hourly)
    elif (type == "twelve"):
        return requests.get(rnk_url_forcast_12hr)
    elif (type == "general"):
        return requests.get(rnk_url_forcast)

# grab 12hr forcast for the week
def getWeeklyForcastTweleveHourData():
    print("requesting 7 day twelve hour forcast")
    forcastResponse = getNationalWeatherServiceAPI("twelve")
    if (forcastResponse.status_code == 500):
        attempt = 1
        print("request failed 500 error")
        while (attempt < 10 and forcastResponse.status_code == 500):
            forcastResponse = getNationalWeatherServiceAPI("twelve")
            attempt += 1
            print("attempting request again: attempt" + str(attempt))
    if (forcastResponse.status_code == 200):
        print("successful response")
        return forcastResponse.json()['properties']

# grab hourly forcast for the week
def getWeeklyForcastHourlyData():
    print("requesting 7 day hourly forcast")
    forcastResponse = getNationalWeatherServiceAPI("hourly")
    if (forcastResponse.status_code == 500):
        attempt = 1
        print("request failed 500 error")
        while (attempt < 10 and forcastResponse.status_code == 500):
            forcastResponse = getNationalWeatherServiceAPI("hourly")
            attempt += 1
            print("attempting request again: attempt" + str(attempt))
    if (forcastResponse.status_code == 200):
        print("successful response")
        return forcastResponse.json()['properties']

# grab hourly forcast for the week
def getWeeklyForcastGeneral():
    print("requesting 7 day General forcast")
    forcastResponse = getNationalWeatherServiceAPI("general")
    if (forcastResponse.status_code == 500):
        attempt = 1
        print("request failed 500 error")
        while (attempt < 10 and forcastResponse.status_code == 500):
            forcastResponse = getNationalWeatherServiceAPI("general")
            attempt += 1
            print("attempting request again: attempt" + str(attempt))
    if (forcastResponse.status_code == 200):
        print("successful response")
        return forcastResponse.json()['properties']

#Parse the data into a List of FullDayForcast objects
def parseData(dataTwelve, dataGeneral):
    periods = dataTwelve['periods']
    list = []
    for period in periods:
        list.append(DayForcast(period['name'], period['shortForecast'], period['detailedForecast'], period['probabilityOfPrecipitation']['value']))

    Monday = FullDayForcast(list[0], list[1], dataGeneral['minTemperature']['values'][0]['value'], dataGeneral['maxTemperature']['values'][0]['value'])
    Tuesday = FullDayForcast(list[2], list[3], dataGeneral['minTemperature']['values'][1]['value'], dataGeneral['maxTemperature']['values'][1]['value'])
    Wednesday = FullDayForcast(list[4], list[5], dataGeneral['minTemperature']['values'][2]['value'], dataGeneral['maxTemperature']['values'][2]['value'])
    Thursday = FullDayForcast(list[6], list[7], dataGeneral['minTemperature']['values'][3]['value'], dataGeneral['maxTemperature']['values'][3]['value'])
    Friday = FullDayForcast(list[8], list[9], dataGeneral['minTemperature']['values'][4]['value'], dataGeneral['maxTemperature']['values'][4]['value'])
    Saturday = FullDayForcast(list[10], list[11], dataGeneral['minTemperature']['values'][5]['value'], dataGeneral['maxTemperature']['values'][5]['value'])
    Sunday = FullDayForcast(list[12], list[13], dataGeneral['minTemperature']['values'][6]['value'], dataGeneral['maxTemperature']['values'][6]['value'])

    return {'Monday': Monday, 'Tuesday': Tuesday, 'Wednesday': Wednesday, 'Thursday': Thursday, 'Friday': Friday, 'Saturday': Saturday, 'Sunday': Sunday}

def gmail_send_message(message_text):
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    #message.set_content("This is automated draft mail")
    message = MIMEText(message_text, 'html')


    message["To"] = emailList
    message["From"] = sender
    message["Subject"] = "Weekly Weather Forcast for Grayson Highlands State Park"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message

def create_message_HTML(WeeklyForcast):
   return """<!DOCTYPE html>
            <html>
            <head>
            <title>
            </title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body style="font-family:Calibri, serif; background-color:#ffffff;background-repeat:no-repeat;background-position:top left;background-attachment:fixed;">
            <h3 style="color:#000000;background-color:#ffffff;">Weather Conditions for the week of """ + currentDate.strftime('%A, %B %d %Y') + """</h3>
            <p style="font-size:14px;font-style:normal;font-weight:normal;color:#000000;background-color:#ffffff;">
                <table class="GeneratedTable" style="width: 100%;
                background-color: #ffffff;
                border-collapse: collapse;
                border-width: 2px;
                border-color: #000000;
                border-style: solid;
                color: #000000;">
                <thead style="background-color: #9ec2b0;">
                    <tr>
                    <th style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"></th>
                    <th style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get("Monday").morningForcast.name+"""</th>
                    <th style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get("Tuesday").morningForcast.name+"""</th>
                    <th style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get("Wednesday").morningForcast.name+"""</th>
                    <th style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get("Thursday").morningForcast.name+"""</th>
                    <th style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get("Friday").morningForcast.name+"""</th>
                    <th style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get("Saturday").morningForcast.name+"""</th>
                    <th style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get("Sunday").morningForcast.name+"""</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><b>Backpacking Conditions<b></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get('Monday').getConditionRating() + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get('Tuesday').getConditionRating() + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get('Wednesday').getConditionRating() + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get('Thursday').getConditionRating() + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get('Friday').getConditionRating() + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get('Saturday').getConditionRating() + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + WeeklyForcast.get('Sunday').getConditionRating() + """</td>
                    </tr>
                    <tr>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><b>Min Temp (F)<b></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Monday').getMinTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Tuesday').getMinTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Wednesday').getMinTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Thursday').getMinTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Friday').getMinTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Saturday').getMinTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Sunday').getMinTemp()) + """</td>
                    </tr>
                    <tr>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><b>Max Temp (F)<b></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Monday').getMaxTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Tuesday').getMaxTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Wednesday').getMaxTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Thursday').getMaxTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Friday').getMaxTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Saturday').getMaxTemp()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Sunday').getMaxTemp()) + """</td>
                    </tr>
                    <tr>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><b>Percipitation %<b></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Monday').getAvgPercip()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Tuesday').getAvgPercip()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Wednesday').getAvgPercip()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Thursday').getAvgPercip()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Friday').getAvgPercip()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Saturday').getAvgPercip()) + """</td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;">""" + str(WeeklyForcast.get('Sunday').getAvgPercip()) + """</td>
                    </tr>
                    <tr>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><b>Conditions<b></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><p style="font-size:12px; ">Throughout the day """ + WeeklyForcast.get('Monday').morningForcast.shortSummaryDay + " In the evening " + WeeklyForcast.get('Monday').eveningForcast.shortSummaryDay + """</p></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><p style="font-size:12px; ">Throughout the day """ + WeeklyForcast.get('Tuesday').morningForcast.shortSummaryDay + " In the evening " + WeeklyForcast.get('Tuesday').eveningForcast.shortSummaryDay + """</p></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><p style="font-size:12px; ">Throughout the day """ + WeeklyForcast.get('Wednesday').morningForcast.shortSummaryDay + " In the evening " + WeeklyForcast.get('Wednesday').eveningForcast.shortSummaryDay + """</p></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><p style="font-size:12px; ">Throughout the day """ + WeeklyForcast.get('Thursday').morningForcast.shortSummaryDay + " In the evening " + WeeklyForcast.get('Thursday').eveningForcast.shortSummaryDay + """</p></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><p style="font-size:12px; ">Throughout the day """ + WeeklyForcast.get('Friday').morningForcast.shortSummaryDay + " In the evening " + WeeklyForcast.get('Friday').eveningForcast.shortSummaryDay + """</p></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><p style="font-size:12px; ">Throughout the day """ + WeeklyForcast.get('Saturday').morningForcast.shortSummaryDay + " In the evening " + WeeklyForcast.get('Saturday').eveningForcast.shortSummaryDay + """</p></td>
                    <td style="border-width: 2px;
                border-color: #000000;
                border-style: solid;
                padding: 3px;"><p style="font-size:12px; ">Throughout the day """ + WeeklyForcast.get('Sunday').morningForcast.shortSummaryDay + " In the evening " + WeeklyForcast.get('Sunday').eveningForcast.shortSummaryDay + """</p></td>
                    </tr>
                </tbody>
            </table>

            <div style="border:solid black;border-width: 1px; margin-top:15px">
                <b style="font-size:16px;font-weight:bold; padding-left:5px">Weather Forcast Details</b>
                <dl id="list" style="font-size:smaller;padding-left:5px">
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Monday").morningForcast.name + """</dt>
                    <dd>""" +  WeeklyForcast.get("Monday").eveningForcast.fullSummaryDay + """</dd>
    
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Monday").eveningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Monday").eveningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Tuesday").morningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Tuesday").morningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Tuesday").eveningForcast.name + """</dt>
                    <dd>"""  + WeeklyForcast.get("Tuesday").eveningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Wednesday").morningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Wednesday").morningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Wednesday").eveningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Wednesday").eveningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Thursday").morningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Thursday").morningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Thursday").eveningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Thursday").eveningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Friday").morningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Friday").morningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Friday").eveningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Friday").eveningForcast.fullSummaryDay + """</dd>
    
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Saturday").morningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Saturday").morningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Saturday").eveningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Saturday").eveningForcast.fullSummaryDay+"""</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Sunday").morningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Sunday").morningForcast.fullSummaryDay + """</dd>
        
                    <dt style="font-weight:bold;">""" + WeeklyForcast.get("Sunday").eveningForcast.name + """</dt>
                    <dd>""" + WeeklyForcast.get("Sunday").eveningForcast.fullSummaryDay+"""</dd>
                </dl>
            </div>
            
            <ul>
                <li>
                    <a href="https://reservevaparks.com/web/Facilities/SearchViewUnitAvailabity.aspx">Reservation Site</a>
                </li>
                <li>
                    <a href="https://www.dcr.virginia.gov/state-parks/grayson-highlands">State Park Page</a>
                </li>
                <li>
                    <a href="https://www.mountain-forecast.com/peaks/Mount-Rogers/forecasts/1746">Mountain Forcaster</a>
                </li>
            </ul>
            <center><img src="https://www.dcr.virginia.gov/state-parks/image/data/gh-mountainview.jpg" alt="Mount Rodgers" style="padding:10px"></center>
            </p>
            </body>
            </html>
            """

# Main
local = datetime.today()
print("Today's date: ", local.strftime('%A, %B %d %Y %X'))

forcastTwelve = getWeeklyForcastTweleveHourData()
forcastGeneral = getWeeklyForcastGeneral()

print("Formating Data")
WeeklyForcast = parseData(forcastTwelve, forcastGeneral)
print("Data formatted")

message = create_message_HTML(WeeklyForcast)
print("html message created")

print("sending gmail message")
gmail_send_message(message)
