# AlfredAI

Physical (Version 2) of AlfredAI was started on August 11, 2024.
This repository was made from a private repository, so the dates for the new features here may be off from when they were actually implemented.

# About

Alfed is an AI built by Harper Bledsoe which uses the OpenAI API in order to be an LLM. However, the OpenAI API is just the framework that the bot is built from. The chatbot has custom built commands which interact with the API in order to accomplish tasks.

The bot is built with modularity and customization in mind. The main script, alfredBrain.py is a class which has functions in it. These functions all contain the abilities he has. So, you could program whatever input device you desire, such as a microphone/speaker, SMS input, or something else and just reference the Brain and it will handle the task.

# Table of Contents
- [Libraries Used](#Libraries-Used)
    - [OpenAI](#OpenAI)
    - [Preinstalled Python 3 Libraries](#Preinstalled-Python-3-Libraries)
    - [PathLib](#PathLib)
    - [SMTPlib](#SMTPlib)
    - [SSL](#SSL)
    - [Pygame](#Pygame)
    - [Langchain](#Langchain)
    - [IMAPlib](#IMAPlib)
    - [Pushsafer](#Pushsafer)
    - [Google Cloud (Firestore, Pubsub)](#Google-Cloud-(Firestore,-Pubsub))
    - [Paho MQTT](#Paho-MQTT)
- [Callable Abilities](#Callable-Abilities)
- [Determining whether the bot called a function](#determining-whether-the-bot-called-a-function)
- [Design](#design)
  

# Libraries Used

## OpenAI

[API Reference](https://platform.openai.com/docs/api-reference/introduction?lang=python)

The main library used for LLM response and AI features. 
To install, run:
```
pip install openai
```

## Preinstalled Python 3 Libraries
- [OS](https://docs.python.org/3/library/os.html)
- [Sys](https://docs.python.org/3/library/sys.html)
- [Json](https://docs.python.org/3/library/json.html)
- [Datetime](https://docs.python.org/3/library/datetime.html)
- [Time](https://docs.python.org/3/library/time.html)
- [Subprocess](https://docs.python.org/3/library/subprocess.html)
- [http.client](https://docs.python.org/3/library/http.client.html)
- [urllib](https://docs.python.org/3/library/urllib.html)


## PathLib

[Documentation](https://docs.python.org/3/library/pathlib.html)

Allows navigation through files, directories, and the system itself.
To install, run:
```
pip install pathlib
```

## SMTPlib

[Documentation](https://docs.python.org/3/library/smtplib.html)

Allows messaging through emails.
This library is automatically installed in Python.

## SSL

[Documentation](https://docs.python.org/3/library/ssl.html)

Allows securing connections with sockets.

## Pygame

[Documentation](https://www.pygame.org/docs/)

Controls everything related to volume, such as speaking the TTS (.wav) files.
To install, run:
```
pip install pygame
```

## Langchain

[Documentation](https://python.langchain.com/docs/integrations/tools/google_search/)

Enables Google searching to find information.

## IMAPlib

[Documentation](https://docs.python.org/3/library/imaplib.html)

Adds ability to check the inbox of a certain email with the given username and password.

## Pushsafer

[Documentation](https://www.pushsafer.com/)

Allows Python to send a push notification to a specified device via a mobile app.

## Google Cloud (Firestore, Pubsub)

[Documentation](https://cloud.google.com/python/docs/reference)

Adds the ability to store information in a cloud database instead of on-device.

## Paho MQTT

[Documentation](https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html)

Allows MQTT messaging from the Raspberry Pi to other devices.


# Callable Abilities:

**_abilities list updated as of 8/19/24_**

1. Sends an email.

```
sendEmail(Requires: String Message, String Recipient)
```

2. Generates TTS audio in an MP3 file.

```
generate_and_save_audio(Requires: String Text To Generate for)
```

3. Plays MP3 audio. This is mainly used for TTS.

```
play_audio(Requires: String File Path of MP3)
```

4. Deletes audio file. This is to save storage after the chatbot has spoken for TTS.

```
delete_audio(Requires: String File Path of MP3)
```

5. Gets a list of the txt files in the _/DataStorage_ file. This is basically the "memory" or storage of Alfred.

```
get_txt_files()
```

6. Reads the contents of a selected file.

```
readSelectedFile(Requires: String Name of File [NO PATH, NO .TXT])
```

7. Appends the input text to the file.

```
editSelectedFile(Requires: String Name of File, String Text to Add)
```

8. Reads a specific saved reminders list in order to display.

```
read_tasks()
```

9. Removes a task from the reminders list.

```
remove_task(Requires: String Name of Task)
```

10. Adds a task to the reminders list.

```
add_task(Requires: String Task Description)
```

11. Lists everything on the current reminders list. This defaults to only listing the reminders for that day, but by changing the wantsAllReminders bool you can list all of them.

```
checkForDueReminders(String: targetTime, String: targetDate, Bool: wantsAllReminders)
```

12. Pulls unread emails from inbox

```
check_unread_emails()
```

13. Pulls any and all data from storage/memory

```
surfThroughMemory()
```

14. Gets current date and time

```
getTodaysDate()
```

15. Gets most recent health data from file. This was collected and stored in the file from another script that pulls Oura Ring data.

```
pullHealthData(String: dateOfDataNeeded)
```

16. Messages my Raspberry Pi plant system I have in order to control the UV light and water.

```
messagePlantSystem(String: msgCommand)
```

17. Pulls the top search result from a web scrape

```
webScrape(String: userInput)
```

18. Acts on the request to call a function. After finding out that the LLM called a function, you can run this, and the Brain will figure out what function the AI wants to call and will execute it. This returns a string reply from the chatbot.
`NOTE: Determining whether the LLM called a function or not must be written in your own code. Examples of this are shown below about how to implement it.`

```
actOnFunctionCall(Requires: OpenAI.completion Response (output), String UserInput)
```

19. This is the main code in order to get a response from the chatbot. You can simply call this with your message.

```
getChatbotResp(Requires: String UserInput Message)
```

# Determining whether the bot called a function

The code to do this can be simplified to:

```
output = alfredBot.getChatbotResp(userInput)
if(output == None):
  print("Called a function")
  botReply = alfredBot.actOnFunctionCall(output, userInput)
  print(botReply)
else:
  print("Did not call a function")
  print(output.content) #print the specific thing the bot said, not just the whole completion response
```

This is because the content of an OpenAI Completion Response is None if it decides to call a function. However, if it doesn't call a function, the output is not empty so you can call the .content of it.

# Design

All of the functionality of Alfred is built into his brain. This is the AlfredBrain.py script. In it, there is an Alfred Brain class that holds all of the capabilities of Alfred listed above. The Brain **IS** Alfred. So basically, every other Python script that uses Alfred just calls the Brain. It is built with simplicity and modularity.

### Example workflow:

![Screenshot 2024-09-06 at 5 11 03 PM](https://github.com/user-attachments/assets/9b3af6e7-ba76-4ac3-8ec1-91bc4db23cb0)
