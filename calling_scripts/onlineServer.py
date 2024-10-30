from flask import Flask, render_template, request, abort, jsonify
import sys
sys.path.insert(1, '/home/harpbled/AlfredAI')
sys.path.insert(1, '/home/harpbled')
import loadApiKeys
import alfredBrain as a
from flask_httpauth import HTTPBasicAuth
from werkzeug.serving import WSGIRequestHandler
import os

auth = HTTPBasicAuth()

username = os.getenv('HTTPS_USERNAME')
password = os.getenv('HTTPS_PASSWORD')

routeOnline = os.getenv('ROUTE_ONLINE')
routePython = os.getenv('ROUTE_PYTHON')
routeSwift = os.getenv('ROUTE_SWIFT')
routeGetMsgs = os.getenv('RESPONSE_ROUTE')

piHostIP = os.getenv('PI_HOST_IP')

users = {
    username: password
}

app = Flask(__name__, template_folder='/home/harpbled/AlfredAI/calling_scripts')

#trusted_proxies = ('192.168.1.254')

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username



@app.route(routeOnline)
@auth.login_required
def index():
    return render_template('alfredOnline.html')

@app.route(routeGetMsgs, methods=['POST'])
def chat():
    user_message = request.form['user_message']
    response = a.alfredBot.getChatbotResp(str(user_message))
    if(response != 'togAudio'):
        if(response.content == None):
            print('called function!')
            botReply = a.alfredBot.actOnFunctionCall(response, user_message)
            print(str(botReply))
            return str(botReply)
        else:
            print("didnt call any functions")
            print(response.content)
            return response.content
    else:
        return 'Changed audio output setting'

@app.route(routePython, methods=['POST'])
def pythonInput():
    data = request.get_json()
    # Process the incoming JSON data
    user_message = data['message']
    response = a.alfredBot.getChatbotResp(str(user_message))
    if(response != 'togAudio'):
        if(response.content == None):
            print('called function!')
            botReply = a.alfredBot.actOnFunctionCall(response, user_message)
            print(str(botReply))
            return jsonify(str(botReply))
        else:
            print("didnt call any functions")
            print(response.content)
            return jsonify(response.content)
    else:
        return 'Changed audio output setting'
    
@app.route(routeSwift, methods=['POST'])
def swiftInput():
    user_message = request.get_json()['text']
    response = a.alfredBot.getChatbotResp(str(user_message))
    if(response != 'togAudio'):
        if(response.content == None):
            print('called function!')
            botReply = a.alfredBot.actOnFunctionCall(response, user_message)
            print(str(botReply))
            return jsonify({'text': botReply})
        else:
            print("didnt call any functions")
            print(response.content)
            return jsonify({'text': response.content})
    else:
        return 'Changed audio output setting'


a.alfredBot.sendEmail("AlfredAI webserver is back online!", emailSubj="AlfredAI Server Message")
#a.alfredBot.set_volume(75)
app.run(debug=True, host=piHostIP, port=5009)