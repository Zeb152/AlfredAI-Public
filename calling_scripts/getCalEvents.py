import datetime
import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

eventsList = []

now = datetime.datetime.now()
yesterday = now - datetime.timedelta(days=1)
tomorrow = now + datetime.timedelta(days=1)
maxTimeTomorrow = now + datetime.timedelta(days=2)

nowStr = now.strftime("%Y-%m-%d")
yesterdayStr = yesterday.strftime("%Y-%m-%d")
tomorrowStr = tomorrow.strftime("%Y-%m-%d")

def main():
  """Shows basic usage of the Google Calendar API.
  Prints and stores all events from yesterday, today, and tomorrow.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens... (unchanged)
  if os.path.exists("/home/harpbled/token.json"):
    creds = Credentials.from_authorized_user_file("/home/harpbled/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "/home/harpbled/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("/home/harpbled/token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    print("Getting events from yesterday, today, and tomorrow")

    events_result = (
      service.events()
        .list(
            calendarId="primary",
            timeMin=yesterday.isoformat() + "Z",
            timeMax=maxTimeTomorrow.isoformat() + "Z",
            maxResults=15,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print(f"No events found.")
      

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"{start} - {event['summary']}")

        print("start: ", start)
        print(start.split('T'))

        eventDateStr = start.split('T')

        print('event date: ', eventDateStr[0])

        #print('DATE STR: ', date_str)
        print("YESTEERDAR: ", yesterdayStr)
        print('TOD: ', nowStr)
        print('TMR: ', tomorrowStr)
        # Check for event date and append details
        if eventDateStr[0] == yesterdayStr:
          print("=====================EVENT YESTERDAY!!")
          appendedEvent = {
            "start_event_time": "YESTERDAY, " + eventDateStr[0],
            "event_details": event['summary']
          }
          eventsList.append(appendedEvent)
        if eventDateStr[0] == nowStr:
          print("=====================EVENT TODAY!!")
          appendedEvent = {
            "start_event_time": "TODAY, " + eventDateStr[0],
            "event_details": event['summary']
          }
          eventsList.append(appendedEvent)
        if eventDateStr[0] == tomorrowStr:
          print("=====================EVENT TOMORROW!!")
          appendedEvent = {
            "start_event_time": "TOMORROW, " + eventDateStr[0],
            "event_details": event['summary']
          }
          eventsList.append(appendedEvent)

    #print("EVENTS: ", eventsList)
    return eventsList

  except HttpError as error:
    print(f"An error occurred: {error}")


  



