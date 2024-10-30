import requests
import speech_recognition as sr
import os
import sys
sys.path.insert(1, '/home/harpbled/AlfredAI')
sys.path.insert(1, '/home/harpbled')
import loadApiKeys
import alfredBrain as a
import ssl
import json
ssl._create_default_https_context = ssl._create_unverified_context

#file to access audio recorded
wav_file_path = "whisperAudio.wav"

os.environ['SDL_AUDIODRIVER'] = 'pulseaudio'

#host address link for speech processing
url = os.getenv("DESKTOP_WHISPER_URL")

def delete_audio(file_path):
    os.remove(file_path)
    print(f"Deleted {file_path}")

def listenToSpeech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        print("Finished listening")

        with open("whisperAudio.wav", "ab") as f:
            f.write(audio.get_wav_data())

def send_wav():
    with open(wav_file_path, 'rb') as f:
        files = {'file': ('audio.wav', f, 'audio/wav')}
        response = requests.post(url, files=files)

        if response.status_code == 200:
            print("File sent successfully.")
            data = json.loads(response.text)
            # Access the main text
            audioToText = data['text']['text']  # Access the nested 'text' key
            return audioToText
        else:
            print("Error sending file:", response.status_code)

def listenAndConvert():
    #a.alfredBot.sendPushNotif('listening!')
    listenToSpeech()
    #a.alfredBot.sendPushNotif('sending wav')
    resp = send_wav()
    print(f"<Resp: {resp}>")
    #a.alfredBot.sendPushNotif('user input: ', resp)
    delete_audio(wav_file_path)
    return resp

            
while True: 
    user_message = listenAndConvert()
    if(user_message != None):
        response = a.alfredBot.getChatbotResp(user_message)
        if(response != 'togAudio'):
            if(response.content == None):
                print('called function!')
                botReply = str(a.alfredBot.actOnFunctionCall(response, user_message))
            else:
                print("didnt call any functions")
                botReply = str(response.content)
            print("<Alfred> " + botReply)
            #a.alfredBot.speakResponse(botReply)
        else:
            print('muted alfred')
    else:
        print('ERROR! GOT NONE FROM STT!')
    #a.alfredBot.sendPushNotif('alfred (MIC): ', botReply)
    #a.alfredBot.speakResponse(botReply)

        


