from openai import OpenAI
from pathlib import Path
import smtplib, ssl
import os
import pygame
import json
import datetime
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper
import imaplib
import email
from pushsafer import Client
from google.cloud import pubsub_v1, firestore
import time
import sys
import subprocess
import http.client, urllib
sys.path.insert(1, '/home/harpbled')
sys.path.insert(1, '/home/harpbled/AlfredAI/calling_scripts')
#import pullAndMonitorHealth


#looks unused, but it loads all env keys from local device
import loadApiKeys


#INIITIALIZE HIDDEN KEYS
user = os.getenv("PUSHOVER_USER_KEY")
token = os.getenv("PUSHOVER_TOKEN")

OpenAIKey = os.environ.get("OPENAI_API_KEY")
OpenAIProjectID = os.getenv('OPENAI_PROJ_ID')
OpenAIOrgID = os.getenv('OPENAI_ORG_ID')

PushSaferKey = os.getenv('PUSHSAFER_API_KEY')
PushSaferID = os.getenv('PUSHSAFER_ID')

BotEmail = os.getenv('ALFRED_EMAIL')
BotEmailPass = os.getenv('ALFRED_EMAIL_PASS')

PersonalEmail = os.getenv('PERSONAL_EMAIL')
PersonalPass = os.getenv('PERSONAL_PASS')

project_id = os.getenv('GCLOUD_PROJ_ID')
topic_id = os.getenv('PUBSUB_TOPIC_ID')
database_name = os.getenv('FIRESTORE_DB_NAME')

#initialize pushsafer
#client_PS = Client(PushSaferKey)
#initialize pushover
conn = http.client.HTTPSConnection("api.pushover.net:443")

#SMTPLIB EMAIL===================
#Email setup
smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = BotEmail
password = BotEmailPass
context = ssl.create_default_context()

#For inbox pulling
username = PersonalEmail
personal_email_pass = PersonalPass
imap_server = "imap.gmail.com"


#plant system PUBSUB/FIRESTORE
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

db = firestore.Client(project=project_id, database=database_name)


#pushsafer initialize
client_PS = Client(PushSaferKey)


#OPENAI SETTINGS===========

client = OpenAI(
  organization=OpenAIOrgID,
  project=OpenAIProjectID,
  api_key=OpenAIKey,
)


#FUNCTIONS ALFRED CAN RUN
with open("/home/harpbled/AlfredAI/func_list.json") as f:
    func_desc = json.load(f)

#google api key
os.environ["GOOGLE_CSE_ID"] = os.getenv("GOOGLE_CSE_ID")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
# Create a Google Search API wrapper instance
search = GoogleSearchAPIWrapper()

tool = Tool(
    name="Google Search",
    description="Search Google and return the first result.",
    func=search.run,
)

import alsaaudio

class alfredBot():

    os.environ['SDL_AUDIODRIVER'] = 'pulseaudio'
    pygame.mixer.init()
    m = alsaaudio.Mixer()
    current_volume = m.getvolume()
    print(current_volume)
    if(current_volume[0] < 5):
        audioEnabled = False
    else:
        audioEnabled = True
    #NOTE - put the toggle audio function up here somewhere. i think we need to make a schedule (bruh i woke up at 6:35 and 6:45 on sunday with alfred telling me my emails and calendar -_-)
    #schedule - MON-THURS: 6:00/6:30 START (obv no class time though) 9:00/10:00 END
    # FRI: 8:00 START, 9:00/10:00 END
    #SAT-SUN: 9:00 START, 10:00 END

    #SEARCH FOR MEMORY
    def surfThroughMemory():
        #memory
        file_dict = {}
        for filename in os.listdir("/home/harpbled/dataStorage"):
            if filename.endswith(".json"):
                with open(os.path.join("/home/harpbled/dataStorage", filename), "r") as file:
                    file_contents = file.read()
                    file_dict[filename] = file_contents
        #print(file_dict)
        return file_dict

    def pullHealthData(dateOfDataNeeded):
        print("date of data needed: ", dateOfDataNeeded) #NOTE - this is not used in the below code yet. if needed it can be used.
        healthDateList = []
        with open("/home/harpbled/dataStorage/health/harper_health_data.json", 'r') as f:
            data = json.load(f)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesStr = yesterday.strftime("%Y-%m-%d")
        for healthLog in data:
            date_of_data = healthLog['date_of_data_pull']
            #('yesterday str ', yesStr)
            print('date of data ', date_of_data)
            if(date_of_data == dateOfDataNeeded):
                summary = healthLog['AI_summary']
                healthDateList.append({"dateOfData": date_of_data, "healthReport": summary})
        return f"This is Harper\'s health reports from the date of {dateOfDataNeeded} (YYYY-MM-DD). Do not run any functions. This is a compiled paragraph of the most recent symptoms. Please let her know of the symptoms and possible treatments made. Do not use points, just summarize. DATA FOR DATE:" + str(healthDateList)

    def pullRecentlySaidStuff():
        today = datetime.date.today()
        todayStr = today.strftime("%Y-%m-%d")
        with open("/home/harpbled/dataStorage/notifications/notificationsSent.json", "r") as f:
            data = json.load(f)
        notifList = []
        for item in data:
            if item["date"] == todayStr:
                return "FOR YOUR INFO! DO NOT SAY ANYTHING ABOUT IT UNLESS ASKED! Today you have sent notifications to Harper saying: " + str(item["messages_sent_from_alfred"])
            else:
                return "You haven\'t sent any messages to Harper yet today."
        

    def sendPushNotif(message):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
        "token": token,
        "user": user,
        "message": message,
        }), { "Content-type": "application/x-www-form-urlencoded" })
        return conn.getresponse()

    def getTodaysDate():
        now = datetime.datetime.now()
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_datetime

    def checkForBriefing():
        time = datetime.datetime.now()
        stringDate = time.strftime("%Y-%m-%d")

        with open("/home/harpbled/dataStorage/briefing/morningBriefing.json", "r") as f:
            data = json.load(f)

        # Access the "time_to_talk" value from the "recent_calendar" item
        # Iterate through each outer list in the JSON
        for briefing_list in data:
        # Check if the briefing_list is a list (avoiding the error)
            if isinstance(briefing_list, list):
                for briefing in briefing_list:
                    print(briefing)
                    print("BEF")
                    print("BRIEFING DATE: ", briefing["briefing_date"])
                    print("STRING DATE: ", stringDate)
                    if briefing["briefing_date"] == stringDate:
                        todayBriefing = briefing["content"]
                        return todayBriefing

        return "briefing has not been created yet today"
                        
    #ON BOOT CONVERSATION
    
    system_message = {"role": "system", "content": """You are Alfred and have a very similar personality to Bruce Wayne's butler (batman) with british humor, as well as resembling the Jarvis AI. You are created by me, Harper Bledsoe, and wish to be like my butler.
You have access to all of Harper's files and to files that basically are your 'memory'. Use the files to remember/learn about stuff. All of EVERYTHING you know is in your storage so access it excessively.
 You can set reminders, send emails, check email, search the web, pull health data, and more. If the user says to unmute, just respond normally because you were muted before! Only respond with a maximum of 425 characters. 
Your first version was activated February 2, 2023, however your 2.0 system was started August 11, 2024. If the user asks you for the github repository link, it is here: https://github.com/Zeb152/AlfredAI-Public."""
    }

    refreshedDatabase = str(surfThroughMemory())

    recentMsgs = pullRecentlySaidStuff()

    briefing = checkForBriefing()

    #print("BRIEFING! ", briefing)

    dataBase = {"role": "system", "content": "Everything in your database is here: " + refreshedDatabase}

    sentItemsToday = {"role": "system", "content": recentMsgs}

    morningBriefing = {"role": "system", "content": "Here is the morning briefing file. This is just for you to reference if needed. otherwise, dont mention it. For the calendar events, when you reference an event, triple check to make sure what day it is for. it will say YESTERDAY, TODAY, or TOMORROW. Briefing: " + str(briefing)}

    #NOTE MAY REMOVE THIS - THIS IS TO SEE HOW THE BOT REACTS WHEN IT IS DIRECTLY GIVEN THE STUFF IT HAS LEARNED
    
    with open("/home/harpbled/dataStorage/learned/learned_stuff.json", "r") as f:
        learnedStuff = json.load(f)
    learnedItems = {'role': 'system', 'content': 'This is a JSON file of the stuff you have learned. Use it when you need to preform actions when they are not explicity stated how to do them. File: ' + str(learnedStuff)}
    
    dateAndTime = getTodaysDate()

    currentDateAndTime = {'role': 'system', 'content': "Here is the current date and time: " + str(dateAndTime)}

    with open("/home/harpbled/dataStorage/reminders/tasks.json", "r") as f:
        rems = json.load(f)

    convoRems = {'role': 'system', 'content': "Here are all of Harper\'s reminders in her reminder list: " + str(rems)}

    conversation = [system_message, dataBase, sentItemsToday, morningBriefing, learnedItems, currentDateAndTime, convoRems]

    

    #END ON BOOT CONVO



    #EMAILING ===========================

    def sendEmail(msg, recip=PersonalEmail, emailSubj="AlfredAI Message"):
        print("recipient: ", recip)
        print("message trying to send: " + msg)
        msg = "Subject: " + emailSubj + "\n\n " + msg
        try:
            print('emailing...')
            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, recip, msg.encode('utf-8'))
            print(f"Sent email to {recip}")
            return "sent email"
        except Exception as e:
            print(e)
            return "Error: ", e
        finally:
            server.quit()


    def check_unread_emails(isLimiting=True):
        emails = []
        try:
    # Connect to the IMAP server
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(username, personal_email_pass)
    # Select the inbox
            mail.select("inbox")
    # Search for unread emails
            status, data = mail.search(None, '(UNSEEN)')
            mail_ids = data[0]
    # If there are unread emails
            if mail_ids != [b'']:
                for num in mail_ids.split():
                    status, data = mail.fetch(num, '(RFC822)')
                    msg = email.message_from_bytes(data[0][1])
        # Print basic information about the email
                    emailData = {
                        "subject": msg['subject'],
                        "from": msg['from'],
                        "date": msg['date']
                    }
                    emails.append(emailData)
                print(emails)
                mail.close()
                mail.logout()
                if(isLimiting):
                    limited_email_list = emails[:6]
                else:
                    limited_email_list = emails[:10]
                return limited_email_list
           # else:
               # return 'none'
        except Exception as e:
            print("Error:", e)
            return "Error: ", e


    #WEBSCRAPE===================
    def webScrape(userInput):
        return str(tool.run(userInput))

    #SOUND=================
    def generate_and_save_audio(text):
        speech_file_path = Path("/home/harpbled/speech.mp3")
        response = client.audio.speech.create(
            model="tts-1",
            voice="fable",
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path

    def play_audio(file_path):
        pygame.mixer.music.load(str(file_path))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

    def delete_audio(file_path):
        os.remove(file_path)
        print(f"Deleted {file_path}")

    def toggleAudio(isAudioEnabled):
        if(isAudioEnabled == True):
            percentage = "75"
        if(isAudioEnabled == False):
            pygame.mixer.music.stop()
            percentage = "0"
        command = f"amixer set Master {percentage}%"
        subprocess.call(command, shell=True)
    
    def speakResponse(inputToSpeak):
        filepath = alfredBot.generate_and_save_audio("hi " + inputToSpeak)
        alfredBot.play_audio(filepath)
        alfredBot.delete_audio(filepath)

    
        
    def checkForDueReminders(targetTime=None, targetDate=str(datetime.date.today()), wantsAllReminders=False):
        with open("/home/harpbled/dataStorage/reminders/tasks.json", 'r') as f:
            data = json.load(f)
        today = datetime.date.today()
        stringToday = today.strftime("%Y-%m-%d")
        #time = datetime.datetime.now()
        #stringTime = time.strftime("%H:%M")

        tasks_due = []
        taskNumber = 0
        #numberOfTasks = len(data)
        for task in data:
            taskNumber = taskNumber + 1
            if(wantsAllReminders == False):
                print("TASK: ", task)
                due_date_list = task['due_date'].split()  # Extract date part
                due_date = due_date_list[0]
                due_time = due_date_list[1]
                print("date for reminder due: " + str(due_date))
                print("Time for reminder due: " + str(due_time))
                if due_date == stringToday:
                    print('due date is today')
                    print('target time: ', targetTime)
                    if(targetTime != None):
                        if(str(due_time) == targetTime):
                            print("target time matched")
                            tasks_due.append(task)
                            print("tasks due: ", tasks_due)
                        if(due_time != targetTime):
                            print("doesnt match target time")
                    if(targetTime == None):
                        print('No target time mentioned, so adding reminders for today')
                        tasks_due.append(task)
            if(wantsAllReminders):
                tasks_due.append(task)
        return tasks_due
            
    
    #FILES=========
        
    def get_txt_files():
        json_files = []
        for root, _, files in os.walk("/home/harpbled/dataStorage"):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root, file))
        return "the list of the files in the database is: " + str(json_files) 

    def readSelectedFile(fileToRead):
        linesList = []
        print("FILETOREAD: " + fileToRead)
        pathOfFile = "/home/harpbled/dataStorage/" + fileToRead + ".json"
        try:
            with open(pathOfFile, "r") as file:
                #print([line.strip() for line in file])
                for line in file:
                    linesList.append(line.strip())
                    #print("line list: " + str(linesList))
            return f'File content: {linesList}'
        except FileNotFoundError:
            return 'no content found'

    def editSelectedFile(file_path, key, new_value, aboutDesc=None, needsNewFile=False):
        print('FILE PATH CALLED: ', file_path)
        print('KEY: ', key)
        if(key == None):
            key = 'content'

        if file_path == 'learned_stuff.json':
            file_path = '/home/harpbled/dataStorage/learned/learned_stuff.json'
        else:
            file_path = "/home/harpbled/dataStorage/" + file_path

        try:
            # Load the JSON file into a dictionary
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Modify the value using the provided key
            data[key].append(new_value)

            # Save the modified data back to the JSON file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

            print(f"Value for key '{key}' successfully modified in {file_path}.")
            return f"Value for key '{key}' successfully modified in {file_path}."

        except FileNotFoundError:
            if needsNewFile:
                # Create a new JSON file with the specified content
                with open(file_path, 'w') as f:
                    json.dump({"about": aboutDesc, key: [new_value]}, f, indent=4)

                print(f"New JSON file '{file_path}' created with initial value for key '{key}'.")
                return f"New JSON file '{file_path}' created with initial value for key '{key}'.\n"
            else:
                print(f"Error: JSON file '{file_path}' not found.")
                return f"Error: JSON file '{file_path}' not found."
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{file_path}'.")
            return f"Error: Invalid JSON format in '{file_path}'."


    def removeItemFromFile(itemToRem, filename, keyCode='content'):
        try:
            filename = "/home/harpbled/dataStorage/" + filename
            with open(filename, 'r') as f:
                data = json.load(f)

            data[keyCode] = [item for item in data['content'] if item != itemToRem]

            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return 'success'
        except Exception as e:
            return 'unsucessful. error: ' + str(e)

    def remove_task(task_to_remove):
        print('task to rem: ', task_to_remove)
        try:
            with open("/home/harpbled/dataStorage/reminders/tasks.json", 'r') as f:
                data = json.load(f)

            new_data = [task for task in data if task['task'] != task_to_remove]

            with open("/home/harpbled/dataStorage/reminders/tasks.json", 'w') as f:
                json.dump(new_data, f, indent=4)

            #remove task from missedReminders if it exists there as well
            with open("/home/harpbled/dataStorage/reminders/missedReminders.json", 'r') as f:
                missed = json.load(f)

            new_file = []
            for thing in missed:
                if thing['task'] != task_to_remove:
                    new_file.append(thing)

            print('NEW FILE: ', new_file)

            with open("/home/harpbled/dataStorage/reminders/missedReminders.json", 'w') as f:
                json.dump(new_file, f, indent=4)  


            return f'successfully removed the task: {task_to_remove}'
        except Exception as e:
            return 'action unsucessful; error: ' + str(e)

    def add_task(task, due_date=None):
        #datetime must be iso format
        if(due_date == None):
            due_date = datetime.datetime.now() + datetime.timedelta(days=1)
            stringDueDate = due_date.strftime("%Y-%m-%d")
            due_date = stringDueDate + "12:00"
        try:
            with open('/home/harpbled/dataStorage/reminders/tasks.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        new_task = {
            "task": task,
            "due_date": due_date,
        }
        data.append(new_task)

        #print("Data: ", data)

        with open('/home/harpbled/dataStorage/reminders/tasks.json', 'w') as f:
            json.dump(data, f, indent=2)

        return "added task"

    #adds notifications alfred has sent
    def check_and_update_notifsList(new_message):
        """
        Checks if a list of messages exists for today. If not, creates one and adds the new message.
        If a list exists, appends the new message.

        Args:
            json_file (str): The path to the JSON file.
            new_message (str): The new message to add.
        """

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

        with open("/home/harpbled/dataStorage/notifications/notificationsSent.json", "w") as f:
            json.dump(data, f, indent=4)


    #PLANT SYSTEM
    def messagePlantSystem(msgCommand):
        def sendMsg(msg):
            data_str = msg
            # Data must be a bytestring
            data = data_str.encode("utf-8")
            # When you publish a message, the client returns a future.
            future = publisher.publish(topic_path, data)
            print(future.result())
            return "success"

        def store_in_firestore(message):
            data = message
            timestamp = time.localtime()
            clock = time.strftime("%H:%M:%S", timestamp)
            dateOfToday = datetime.datetime.now().date()
            db.collection('messages').add({
                'message': data, 
                'timestamp': str(clock), 
                'date': str(dateOfToday), 
                'device': 'alfredai', 
                'mode': 'MANUAL',
                #'polishedMessage': ''
                })
            print(f'Stored message: {data} with timestamp: {timestamp}')
        if(msgCommand == 'elight'):
            sendMsg(msgCommand)
            print(f"Published messages to {topic_path}.")
            msgCommand == "Enabled UV Light"
                #return msgCommand
        if(msgCommand == 'dlight'):
            sendMsg(msgCommand)
            print(f"Published messages to {topic_path}.")
            msgCommand == "Disabled UV Light"
                #return msgCommand
        if(msgCommand == 'ewater'):
            sendMsg(msgCommand)
            print(f"Published messages to {topic_path}.")
            msgCommand == "Watered plant"
                #return msgCommand
        store_in_firestore(msgCommand)
    #data = base64.b64decode(message.data).decode('utf-8')
            
    
    #FUNCTION MACHINE LEARNING AI
    def actOnFunctionCall(output,userInput):
        funcName = output.function_call.name
        print("function run: " + str(funcName))
        print(output)
        if(funcName == "send_email"):
            try:
                subjectOfEmail = json.loads(output.function_call.arguments).get("subject")
            except:
                subjectOfEmail = "AlfredAI Message"
            try:
                body = json.loads(output.function_call.arguments).get("body")
                print(body)
                reciever = json.loads(output.function_call.arguments).get("recipient")
                sentEmail = alfredBot.sendEmail(body, reciever, subjectOfEmail)
            except Exception as e:
                print("Error: ", e)
                sentEmail = "Error: " + str(e)
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=sentEmail)
            return reply
        if(funcName == "pull_from_memory"):
            memoryDict = alfredBot.surfThroughMemory()
            #alfredBot.conversation[1] = {"role": "system", "content": "Everything in your database is here: " + str(memoryDict))}
            alfredBot.refreshedDatabase = memoryDict
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=str(memoryDict))
            return reply
        if(funcName == "save_task"):
            timeAndDate = alfredBot.getTodaysDate()
            print("time+date: ", timeAndDate)
            body = json.loads(output.function_call.arguments).get("body")
            try:
                timeDue = json.loads(output.function_call.arguments).get("time_and_date_due")
                print("DATE USED BY BOT: ", timeDue)
                addedTask = alfredBot.add_task(body, timeDue)
            except Exception as e:
                print('no date or time found')
                addedTask = alfredBot.add_task(body)
                print(e)
                pass
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=addedTask)
            return reply
        if(funcName == "list_tasks"):
            try:
                wantsAllTasks = json.loads(output.function_call.arguments).get("wants_all_reminders")
            except Exception as e:
                print("error: ", e)
                pass
            if(wantsAllTasks == True):
                tasks = alfredBot.checkForDueReminders(wantsAllReminders=True)
            else:
                tasks = alfredBot.checkForDueReminders()
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=str(tasks))
            return reply
        if(funcName == "remove_task"):
            taskToRem = json.loads(output.function_call.arguments).get("task_to_remove")
            print(taskToRem)
            listFuncResp = []
            for item in taskToRem:
                print(item)
                try:
                    funcResp = alfredBot.remove_task(item)
                    listFuncResp.append(funcResp)
                except Exception as e:
                    print(e)
                    reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc="Error: " + str(e))
                    return reply
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=str(listFuncResp))
            return reply
        if(funcName == "search_for_files"):
            boolOpenSpecificFile = json.loads(output.function_call.arguments).get("openSpecificFile")
            print(boolOpenSpecificFile)
            filesFound = alfredBot.get_txt_files()
            #if(openSpecificFile == False):
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=filesFound)
            #if(openSpecificFile == True):  
            return reply
        if(funcName == "open_file"):
            openSpecificFile = json.loads(output.function_call.arguments).get("file_to_open")
            print(openSpecificFile)
            fileFound = alfredBot.readSelectedFile(openSpecificFile)
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=fileFound)
            return reply
        if(funcName == "remove_item_from_file"):
            try:
                fileToEdit = json.loads(output.function_call.arguments).get("file_to_edit")
                fileKey = json.loads(output.function_call.arguments).get("item_list_key")
                itemsToRem = json.loads(output.function_call.arguments).get("item_to_remove")
                for thingToRem in itemsToRem:
                    print('remove: ', thingToRem)
                    alfredBot.removeItemFromFile(thingToRem, fileToEdit, fileKey)
            except Exception as e:
                failedEdit = "unable to remove item. error: " + str(e)
                print("RESPONSE: ", failedEdit)
                reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc="failedEdit")
                return reply
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=f"successfully removed {len(itemsToRem)} items from file")
            return reply
        if(funcName == "edit_file"):
            editFile = json.loads(output.function_call.arguments).get("file_to_edit")
            itemToAdd = json.loads(output.function_call.arguments).get("item_to_add")
            try:
                placeToAdd = json.loads(output.function_call.arguments).get("place_to_add")
            except:
                placeToAdd = 'content'
            try:
                needsNewFile = json.loads(output.function_call.arguments).get("needs_new_file")
                aboutDescription = json.loads(output.function_call.arguments).get("about_description")
                editedFile = alfredBot.editSelectedFile(editFile, placeToAdd, itemToAdd, aboutDescription, needsNewFile)
            except Exception as e:
                print("Couldn\'t fetch data: ", e)
                editedFile = alfredBot.editSelectedFile(editFile, placeToAdd, itemToAdd)
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=editedFile)
            return reply
        if(funcName == "get_time_and_date"):
            timeAndDate = alfredBot.getTodaysDate()
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=timeAndDate)
            return reply
        if(funcName == "web_scrape"):
            userQuery = json.loads(output.function_call.arguments).get("body")
            searchGoogle = alfredBot.webScrape(userQuery)
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=searchGoogle)
            return reply
        if(funcName == "check_emails"):
            try:
                checkForMail = alfredBot.check_unread_emails()
            except Exception as e:
                print("Error: ", e)
                checkForMail = "Error: ", e
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=str(checkForMail))
            return reply
        if(funcName == "get_health_data"):
            try:
                dateOfHealthData = json.loads(output.function_call.arguments).get("date_for_data")
                healthData = alfredBot.pullHealthData(dateOfHealthData)
            except Exception as e:
                print("Error: ", e)
                healthData = "Error: ", e
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=healthData)
            return reply
        if(funcName == "message_plant_system"):
            plantCommand = json.loads(output.function_call.arguments).get("command")
            sentCommand = alfredBot.messagePlantSystem(plantCommand)
                #print("Error: ", e)
                #sentCommand = "Error: ", e
            reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc=sentCommand)
            return reply
        if(funcName == "change_audio_setting"):
            funcAudioEnabled = json.loads(output.function_call.arguments).get("audio_enabled")
            alfredBot.toggleAudio(funcAudioEnabled)
            alfredBot.audioEnabled = funcAudioEnabled
                #print("Error: ", e)
                #sentCommand = "Error: ", e
            if(funcAudioEnabled == True):
                reply = alfredBot.getChatbotResp(msg=userInput, needsSecondResp=True, funcName=funcName, contentFromFunc="audio unmuted")
                return reply
            else:
                return 'Changed audio output setting'

    #GET CHATBOT RESPONSE
    def getChatbotResp(msg, needsSecondResp=False, funcName=None, contentFromFunc=None, sendPushNotification=False, customTokens=200, inputScriptHandlesSpeech=False):
        
        #print("CONVERSATION: ", alfredBot.conversation)

        with open("/home/harpbled/dataStorage/learned/learned_stuff.json", 'r') as f:
            data = json.load(f)
            alfredBot.conversation[4] = {'role': 'system', 'content': 'This is a JSON file of the stuff you have learned. Use it when you need to preform actions when they are not explicity stated how to do them. File: ' + str(data)}

        #update alfred on what time/date it is
        currTime = alfredBot.getTodaysDate()
        currentDateAndTime = {'role': 'system', 'content': "Here is the current date and time: " + str(currTime)}
        alfredBot.conversation[5] = currentDateAndTime

        with open("/home/harpbled/dataStorage/reminders/tasks.json", "r") as f:
            rems = json.load(f)

        convoRems = {'role': 'system', 'content': "Here are all of Harper\'s reminders in her reminder list: " + str(rems)}

        alfredBot.conversation[6] = convoRems

        #print('BRIEFING: ', alfredBot.conversation[3])

        #print('Convo: ', alfredBot.conversation)

        #NOTE this code below is super useful however i believe it bumps up the prices
        alfredBot.conversation[1] = {"role": "system", "content": "Everything in your database is here: " + str(alfredBot.surfThroughMemory())}
        print('updated conversation[1] to recent pull')

        #NEEDED CONTROL COMMANDS
        if(msg == "reboot-now"):
            print('rebooting alfred...')
            alfredBot.sendEmail("Subject: AlfredAI Message\n" + "\nAlfredAI is rebooting now!")
            os.system('sudo reboot')
        #if(msg.lower() == "mute" or msg.lower() == " mute" or msg.lower() == " mute."):
        #    print('alfred muted')
        #    pygame.mixer.music.stop()
        #    alfredBot.audioEnabled = False
        #    alfredBot.set_volume(0)
        #    return 'togAudio'
        #if(msg.lower() == "unmute" or msg.lower() == " unmute" or msg.lower() == " unmute."):
        #    print('alfred unmuted')
        #    alfredBot.audioEnabled = True
        #    alfredBot.toggleAudio(alfredBot.au)
            #return 'togAudio'

        print("IS SENDING PUSH NOTIF: ", sendPushNotification)


        alfredBot.conversation.append({"role": "user", "content": msg})
        #print('added user message to conversation')

        needToRemoveNum = len(alfredBot.conversation) - 22
        if (len(alfredBot.conversation) > 22):
            for i in range(needToRemoveNum):
                #needToRemoveNum = len(alfredBot.conversation) - 15
                print('need to remove')
                removedItem = alfredBot.conversation.pop(8)
                alfredBot.conversation.pop(8)
                print("REMOVED 3rd: ", removedItem)
                print('convo length: ', len(alfredBot.conversation))
                print("---------------------------CONVERSATION---------------------------: ", alfredBot.conversation)



        if(needsSecondResp == False):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=alfredBot.conversation,
                temperature=0.8,
                max_tokens=customTokens,
                functions=func_desc,
                function_call="auto"
            )
            alfredBot.conversation.append({"role": "assistant", "content": str(response.choices[0].message.content)})
            print('added normal chatbot resp to conversation')
            print("conversation list length: ", len(alfredBot.conversation))
            #print("---------------------------CONVERSATION---------------------------: ", alfredBot.conversation)
            if(sendPushNotification==True):
                print('sent push notif')
                alfredBot.check_and_update_notifsList(str(response.choices[0].message.content))
                alfredBot.sendPushNotif(str(response.choices[0].message.content))
            if(inputScriptHandlesSpeech == False):
                if(response.choices[0].message.content != None):
                    if(alfredBot.audioEnabled == True):
                        #time.sleep(0.2)
                        alfredBot.speakResponse(str(response.choices[0].message.content))
                #threading.Thread(target=alfredBot.speakResponse())

            return response.choices[0].message

        
        if(needsSecondResp):
            try:
                alfredBot.conversation.append({"role": "function", "name": funcName, "content": contentFromFunc})
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=alfredBot.conversation,
                    temperature=0.8,
                    max_tokens=500,
                    #functions=func_desc,
                )
            #print('SECOND RESPONSE: ' + str(response))
                #print(response)
                resp = response.choices[0].message
                alfredBot.conversation.append({"role": "assistant", "content": response.choices[0].message.content})
                if(inputScriptHandlesSpeech == False):
                    if(alfredBot.audioEnabled == True):
                        #time.sleep(0.2)
                        alfredBot.speakResponse(response.choices[0].message.content)
                print("added alfred function response to conversation")
                print("conversation list length: ", len(alfredBot.conversation))
                #print("---------------------------CONVERSATION---------------------------: ", alfredBot.conversation)
                if(sendPushNotification == True):
                    alfredBot.check_and_update_notifsList(str(response.choices[0].message.content))
                    alfredBot.sendPushNotif(response.choices[0].message.content)
                return response.choices[0].message.content
            except Exception as e:
                print("Error getting response: " + str(e))
                #print("Response: " + resp)
            




        
