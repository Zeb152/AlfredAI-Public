import datetime
import sys
sys.path.insert(1, '/home/harpbled/AlfredAI')
sys.path.insert(1, '/home/harpbled')
import alfredBrain as a
import json
import loadApiKeys
import os
from dateutil.parser import parse
from openai import OpenAI
import random

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

#PushSafer API key here
#client_PS = os.getenv('PUSHSAFER_API_KEY')
#deviceID = os.getenv('PUSHSAFER_ID')



isUsingEmailNotifs = False

time = datetime.datetime.now()
stringDate = time.strftime("%Y-%m-%d")
print('str date: ', stringDate)
stringTime = time.strftime("%H:%M")

print("stringtime: ", stringTime)


def check_and_update_json(new_message):

    today = datetime.date.today().strftime("%Y-%m-%d")

    with open("/home/harpbled/dataStorage/notifications/notificationsSent.json", "r") as f:
        data = json.load(f)

    found = False
    for item in data:
        if item["date"] == today:
            item["messages_sent_from_alfred"].append(new_message)
            found = True
            break

    if not found:
        new_item = {"date": today, "messages_sent_from_alfred": [new_message]}
        data.append(new_item)

    # commented this out due to doubles in json file
        
   # with open("/home/harpbled/dataStorage/notifications/notificationsSent.json", "w") as f: 
   #     json.dump(data, f, indent=4)



def checkAlfred():

    reminders = a.alfredBot.checkForDueReminders(targetTime=stringTime)

    with open("/home/harpbled/dataStorage/reminders/missedReminders.json", "r") as f:
        data = json.load(f)

    today = datetime.date.today()
    stringToday = today.strftime("%Y-%m-%d")

    

    hasMatched = False

    #testing wiping the file everyday at 9 (after notified user about it)
    if(stringTime == "21:00"):
        hasMatched = True
    
    for thing in data:
        print("TASK: ", thing)
        due_date_list = thing['due_date'].split()  # Extract date part
        due_date = due_date_list[0]
        due_time = due_date_list[1]
        print("date for old reminder due: " + str(due_date))
        print("Time for old reminder due: " + str(due_time))
        if due_date == stringToday:
                print('due date is today')
                print('target time: ', stringTime)
                if(stringTime == '20:30'):
                    print('it is not 8:30pm')
                    if(str(due_time) == stringTime):
                        print("target time matched")
                        #NOTE hey future me in case you cant figure out why its not auto reminding of missed reminders at 20:30 its
                        #because of past me right here :D i did this because it was added to the briefing and therefore gets assigned
                        #a random notification time anyway (and a more sophisticated and random time) but uncomment this code if u mad :D
                        #hasMatched = True
                        #reminders.append(thing)
        if due_date < stringToday:
            hasMatched = True
    
    if(hasMatched):
        with open("/home/harpbled/dataStorage/reminders/missedReminders.json", "w") as f:
            wipeFile = []
            json.dump(wipeFile, f, indent=2)
        hasMatched = False


    print("reminders: ", reminders)

    if(reminders == []):
        print("No reminders right now")
        sys.exit()
    if(reminders == None):
        print("No reminders right now")
        sys.exit()
    if(reminders != [] or reminders != None):
        print("Reminders for this time: ", reminders)

        numberOfTasks = len(reminders)

        reminderMessage = "Reminder- "

        taskNumber = 0

        for reminder in reminders:
            taskNumber = taskNumber + 1
            taskName = reminder["task"]
            if(taskNumber != numberOfTasks):
                reminderMessage = reminderMessage + str(taskName) + ", "
            else:
                reminderMessage = reminderMessage + str(taskName) + "!"
        
        check_and_update_json(reminderMessage)

        newReminderMsg = "Do not run any functions. This is an automated message, but reply back as if you were telling Harper this reminder: " + reminderMessage

        resp = a.alfredBot.getChatbotResp(newReminderMsg, customTokens=350)
        smartReminder = resp.content

        if(isUsingEmailNotifs == False):
            #a.alfredBot.speakResponse(smartReminder)
            a.alfredBot.sendPushNotif(smartReminder)
        if(isUsingEmailNotifs):
            emailMessage = "Subject: Alfred AI Reminder\n" + smartReminder
            a.alfredBot.sendEmail(emailMessage)

#TO HARD-CODE IN A TIME YOU DONT WANT THE RANDOM BOT TO USE
usedTimes = ['20:30', '09:00']

def getRandomTime(listToScan):

    print("Used time: ", usedTimes)
        
    prompt = [
        {"role": "system", "content": "You are a simple bot that reads that data in a data list and based on what it is you will output a random time of day that the person may want to see that notification in military time. ONLY OUTPUT ONE TIME - it doesnt matter how many items are in the list. Your output format should be 'TIME: RANDOM_TIME_OF_DAY'. Make it very random times, however do not output times between 14:30-15:30 and 22:00-5:00, and do not output these used times: " + str(usedTimes) + " Example outputs are: 10:04, 13:46, 16:09"},
        {"role": "system", "content": "These are the tasks that were never checked off the list. Make a time (IN THE EVENING, probably somewhere between 8pm-10pm (but do military time) TASKS: " + str(listToScan)},
        {"role": "system", "content": "Do not make the time earlier than the current time. This is the current time: " + str(time)}
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

def checkForMissedTasks():
    with open("/home/harpbled/dataStorage/reminders/missedReminders.json", 'r') as f:
        output_data = json.load(f)

    new_updated = []

    checkUpdated = 0

    fullDatetime = datetime.datetime.now()
    dateStr = datetime.datetime.strftime(fullDatetime, "%Y-%m-%d")

    for item in output_data:
        print('ITEM ', item)
        taskName = item
        if 'due_date' not in item:
            fullTimeForTalking = str(dateStr) + " 20:30"
            newTaskDate = fullTimeForTalking
            new_updated.append({
                "info": "Old reminder that wasn't checked off",
                "task": taskName,
                "due_date": newTaskDate
            })
        else:
            new_updated.append(item)
        checkUpdated = checkUpdated + 1
          # Keep existing tasks unchanged

    with open("/home/harpbled/dataStorage/reminders/missedReminders.json", 'w') as f:
        json.dump(new_updated, f, indent=2)
        

    



def checkForBriefs():

    chatbotResponded = False

    with open("/home/harpbled/dataStorage/briefing/morningBriefing.json", "r") as f:
        data = json.load(f)

    # Access the "time_to_talk" value from the "recent_calendar" item
    # Iterate through each outer list in the JSON
    for briefing_list in data:
    # Check if the briefing_list is a list (avoiding the error)
        if isinstance(briefing_list, list):
            for briefing in briefing_list:
                # Check if the briefing is a dictionary and has "briefing_date"
                if isinstance(briefing, dict) and "briefing_date" in briefing:
                    if briefing["briefing_date"] == stringDate:
                        # Access details and time-to-talk for each item in content
                        for item in briefing["content"]:
                            print('item, ', item)
                            contentFromItem = item['details']['data']
                            timeToTalk = item['details']['time_to_talk']
                            if timeToTalk != 'None':
                                splitTime = timeToTalk.split(' ')
                                timeDue = splitTime[1]
                                print('time due: ', timeDue)
                                if(timeDue == stringTime):
                                    talkAbout = item['name']
                                    print('matches time!!')
                                    resp = a.alfredBot.getChatbotResp("""
                                Alfred, this is an automated message from another python script. This is data from: """ + str(talkAbout) + """.
                                Look at this and inform Harper about it (like, 'I just checked' or 'to keep you updated' or something like that). You are her assistant, 
                                so say it how a normal assistant would. DONT TELL HER WHAT SHE DID YESTERDAY, SHE KNOWS THAT. Use what she did yesterday as an informed prediction of her status.
                                For example: if she just got back from a trip, tell her that she may need to unpack. or, if she worked the day before, you could tell her to submit her work schedule.
                                Here is the data: """ + str(contentFromItem) + """ """, customTokens=700, sendPushNotification=True)
                                    print("<Alfred> ", resp.content)
                                    chatbotResponded = True
            if(chatbotResponded):
                briefing["alfreds_summary"] = str(resp.content)
                check_and_update_json(str(resp.content))
                with open("/home/harpbled/dataStorage/briefing/morningBriefing.json", "w") as f:
                    json.dump(data, f, indent=4)
    

def process_tasks():
    with open("/home/harpbled/dataStorage/reminders/tasks.json", 'r') as f:
        input_data = json.load(f)

    with open("/home/harpbled/dataStorage/reminders/missedReminders.json", 'r') as f:
        output_data = json.load(f)

    past_due_tasks = []
    for task in input_data:
        scheduled_time = parse(task['due_date'])
        print('scheduled!! ', scheduled_time)
        if scheduled_time < datetime.datetime.now():
            print("task:: ", task['task'])
            newTask = {
                "info": "Old reminder that wasn't checked off",
                "task": task['task'],
                "due_date": stringDate + " 20:30"
            }
            if newTask not in output_data:
                past_due_tasks.append(task['task'])
                print('task exceeded date: ', task)
                #input_data.remove(task)
                print('removed old task from present remidners file')
                
    
    #with open("/home/harpbled/dataStorage/reminders/tasks.json", 'w') as f:
    #    f.seek(0)  # Move file pointer to the beginning
    #    json.dump(input_data, f, indent=2)

    output_data.extend(past_due_tasks)

    with open("/home/harpbled/dataStorage/reminders/missedReminders.json", 'w') as f:
        json.dump(output_data, f, indent=2)
        print('added missed tasks to file')


def updateUserHealth():

    #if it is (idk) 9:05am, generate a random time en la mañana to mention my health

    with open('/home/harpbled/dataStorage/health/harper_health_data.json', 'r') as f:
        data = json.load(f)

    #CHANGE LATER FOR RANDOM MORNING TIME!
    mentionHealthTime = "9:57"

    if(stringTime == mentionHealthTime):
        for healthLog in data:
            date_of_data = healthLog['date_of_data_pull']
            #('yesterday str ', yesStr)
            print('date of data ', date_of_data)
            if(date_of_data == stringDate):
                summary = healthLog['AI_summary']
                #healthDateList.append({"dateOfData": date_of_data, "healthReport": summary})

                respSplit = summary.split()

                print(respSplit[0])

                if respSplit[0] == "NEGATIVE:":
                    print('negresp')
                    negative_section = summary.split("NEGATIVE:")[1].split("POSSIBLE-TREATMENTS:")[0].strip()
                    possible_treatments = summary.split("POSSIBLE-TREATMENTS:")[1].strip()
                    print('negative response: ', negative_section)
                    print('\n')
                    print('treatments: ', possible_treatments)

                    a.alfredBot.getChatbotResp(
                        "This is Harper\'s most recent health report. Do not run any functions. This is a compiled paragraph of the most recent symptoms. Please let her know of the symptoms and possible treatments made DO NOT mention any positives to her data; make it clear and concise with the negative. DATA: " + str(negative_section) + "; TREATMENTS: " + str(possible_treatments), 
                        sendPushNotification=True, 
                        customTokens=300
                        )

                else:
                    print(respSplit[0])
                    print("not negative")

updateUserHealth()
checkForBriefs()
process_tasks()
checkForMissedTasks()
checkAlfred()