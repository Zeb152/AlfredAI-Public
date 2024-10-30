import requests
from flask import Flask, request
import json
import speech_recognition as sr
import sys
import os
sys.path.insert(1, '/home/harpbled/AlfredAI')
sys.path.insert(1, '/home/harpbled')
import loadApiKeys
import alfredBrain as a

textbeltKey = os.getenv('TEXTBELT_KEY')
personalNum = os.getenv('PERSONAL_PHONE_NUMBER')
replyWebhook = os.getenv('SMS_WEBHOOK')

#CHANGEABLE CONTROLS ---
#input method - 0 is text computer input, 1 is sms
smsInput = False
developerMode = False
getResponse = True

a.isSendingSms = developerMode


# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

#FLASK======================================

app = Flask(__name__)

def sendMsg(msg):
    params = {
        'phone': personalNum,
        'message': msg,
        'key': textbeltKey,
        'replyWebhookUrl': replyWebhook,
    }
    
    response = requests.post('https://textbelt.com/text', data=params)
    smsResp = response.json()
    if(smsResp['success'] == False):
        print("Failed to send message. Error: " + smsResp['error'])
    #if(smsResp['quotaRemaining'] == 6):
    #    sendMsg("Also, I wanted to let you know that I only have 5 messages left before I run out of quota to reply back.")
    return response.json()
    


def useProcMessage(msg):
    userInput = str(msg)
    print('RECIEVED MESSAGE: ' + userInput)

   #Using AI to determine if functions are needed
    output = a.alfredBot.getChatbotResp(userInput)
    if(output.content == None):
        print('called function!')
        botReply = a.alfredBot.actOnFunctionCall(output, userInput)
        print(str(botReply))
        if(smsInput == True):
            if(developerMode == False):
                #print('sent message but no charge: ' + botReply)
                sendMsg(botReply)
            else:
                print("NOTE: Developer mode enabled. Disable it to text the messages. (This is to save money!)")

    else:
        print("didnt call any functions")
        print(output.content)
        if(smsInput == True):
            if(developerMode == False):
                sendMsg(output.content)
            else:
                print("NOTE: Developer mode enabled. Disable it to text the messages. (This is to save money!)")



convContext = ''
isFollowUpQuestion = False

@app.route('/sms', methods=['POST'])
def handle_sms():
    global isFollowUpQuestion
    global convContext
  # Access incoming SMS data from request.form or request.json
    message = request.json['text']
 
    useProcMessage(message)
    return 'OK'


    
def getInputFromMic():
    with sr.Microphone() as source:
        print("Talk")
        audio_text = r.listen(source)
        print("Time over, thanks")
    # recoginze_() method will throw a request
    # error if the API is unreachable,
    # hence using exception handling
    
        try:
        # using google speech recognition
            print("Text: "+r.recognize_google(audio_text))
            return r.recognize_google(audio_text)
        except Exception as e:
            print("Sorry, I did not get that.")
            print(e)



#MAIN CODE
def chatty():
    if smsInput == False:
        while True:
            #userInput = getInputFromMic()
            userInput = input("> ")
            useProcMessage(userInput)
    elif smsInput == True:
        app.run(debug=True,host="0.0.0.0",port=5000)


if __name__ == '__main__':
    chatty()


    
   
    



