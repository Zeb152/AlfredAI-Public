import sys
sys.path.insert(1, '/home/harpbled/AlfredAI')
sys.path.insert(1, '/home/harpbled')
import alfredBrain as a
import getCalEvents
from openai import OpenAI
import os
import datetime
import json
import random
import loadApiKeys

os.environ['SDL_AUDIODRIVER'] = 'pulseaudio'

#INIITIALIZE HIDDEN KEYS
OpenAIKey = os.environ.get("OPENAI_API_KEY")
OpenAIProjectID = os.getenv('OPENAI_PROJ_ID')
OpenAIOrgID = os.getenv('OPENAI_ORG_ID')

client = OpenAI(
  organization=OpenAIOrgID,
  project=OpenAIProjectID,
  api_key=OpenAIKey,
)

print('fetching calendar...')
failedCalPull = False
 
try:
    calendarList = getCalEvents.main()
except Exception as e:
    failedCalPull = True
    calendarList = str(e)
    print('Failed to pull calendar. Error: ' + calendarList)

print('fetching emails...')
unreadEmailsList = a.alfredBot.check_unread_emails(isLimiting=False)

usedTimes = []

today = datetime.datetime.now()
todayStr = datetime.datetime.strftime(today, "%Y-%m-%d")

time= datetime.datetime.strftime(today, "%H:%M:S")




def getRandomTime(listToScan, timeOfDay=random.randint(1, 3)):

    print("Used time: ", usedTimes)

    #timeOfDay = random.randint(1, 3)
    print('time of day: ', timeOfDay)
        
    prompt = [
        {"role": "system", "content": "You are a simple bot that reads that data in a data list and based on what it is you will output a random time of day that the person may want to see that notification in military time. ONLY OUTPUT ONE TIME - it doesnt matter how many items are in the list. Your output format should be 'TIME: RANDOM_TIME_OF_DAY'. Make it very random times, however do not output these used times: " + str(usedTimes) + " Example outputs are: 10:04, 13:46, 16:09"},
        {"role": "system", "content": "This is a random 1-3 number. If the number is 1, the time should be in the morning . If it is 2, the time should be in the afternoon. If it is 3, the time should be in the evening. NUMBER: " + str(timeOfDay)},
        {"role": "system", "content": "Do not make the time earlier than the current time. This is the current time: " + str(time)},
        #This is the hard coded rules for when to say the briefing. Right now, it won't remind during specified class times and a specified sleep time.
        {"role": "system", "content": "Do not output any times in between 07:00-08:25, 08:30-09:55, 10:00-11:25, 14:30-15:30 and 22:00-6:00. All other times are okay."}
        ]

    prompt.append({"role": "user", "content": str(listToScan)})

    print('prompt: ', prompt)

    print('pending openai...')

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=prompt,
        temperature=0,
        max_tokens=150,
    )

    print('resp: ', response)

    prompt.remove(prompt[1])

    #get time from bot
    botResp = response.choices[0].message.content
    print(botResp)
    splitTime = botResp.split(": ")
    timeForTalking = splitTime[1]
    usedTimes.append(timeForTalking)

    #get current date
    fullDatetime = datetime.datetime.now()
    dateStr = datetime.datetime.strftime(fullDatetime, "%Y-%m-%d")
    #print(dateStr)

    #add those together to get one format
    fullTimeForTalking = str(dateStr) + " " + timeForTalking
    #print("STRING: ", fullTimeForTalking)
    #datetimeTimeTalking = datetime.datetime.strptime(fullTimeForTalking, "%Y-%m-%d %H:%M:%S")
    #print("DATETIME: ", datetimeTimeTalking)

    return fullTimeForTalking
    
#CALENDAR EVENTS
if(failedCalPull == False):
    calendarTime = getRandomTime(calendarList, timeOfDay=1)
    print("CALENDAR TIME: ", calendarTime)
else:
    calendarTime = "Failed to pull calendar events so no time scheduled"


#UNREAD EMAILS
print("len unread emails: ", len(unreadEmailsList))

if(len(unreadEmailsList) > 0):
    emailTime = getRandomTime(unreadEmailsList)
    print("EMAIL TIME: ", emailTime)
else:
    print('Email list is empty')
    emailTime = "None"
    unreadEmailsList = "No unread emails"

#MISSED REMINDERS
with open("/home/harpbled/dataStorage/reminders/missedReminders.json", "r") as f:
    missedRems = json.load(f)

if(len(missedRems) != 0):
    missedRemsTime = getRandomTime(missedRems, timeOfDay=3)
else:
    missedRems = "No missed reminders"
    missedRemsTime = "None"



with open('/home/harpbled/dataStorage/briefing/morningBriefing.json', 'r') as f:
    data = json.load(f)

#to keep the file smaller than it needs to be. this keeps only the previous 2 weeks of briefings.
print(f'data length: {len(data)}')
if len(data) > 15:
    print('too many morning briefings')
    data.pop(0)  # This removes the first item in the list
    print('removed the first item')




briefing = [
    {
        "briefing_date": todayStr,
        "content": [
            {
                "name": "recent_calendar",
                "details": {
                    "data": calendarList,
                    "time_to_talk": calendarTime
                }
            },
            {
                "name": "recent_emails",
                "details": {
                    "data": unreadEmailsList,
                    "time_to_talk": emailTime
                }
            },
            {
                "name": "missed_reminders_notified",
                "details": {
                    "data": missedRems,
                    "time_to_talk": missedRemsTime
                }
            }
        ]
    }
]


data.append(briefing)

with open('/home/harpbled/dataStorage/briefing/morningBriefing.json', 'w') as f:
    json.dump(data, f, indent=2)

#print(briefing)

    