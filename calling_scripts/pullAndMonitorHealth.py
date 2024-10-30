from openai import OpenAI
import datetime
import pandas as pd #pandas in the future??
import sys
sys.path.insert(1, '/home/harpbled/AlfredAI')
sys.path.insert(1, '/home/harpbled')
import loadApiKeys
import alfredBrain as a
import ouraPull
import json
import os

os.environ['SDL_AUDIODRIVER'] = 'pulseaudio'

OpenAIKey = os.getenv('OPENAI_API_KEY')
OpenAIProj = os.getenv('OPENAI_PROJ_ID')
OpenAIOrg = os.getenv('OPENAI_ORG_ID')

client = OpenAI(
  organization=OpenAIOrg,
  project=OpenAIProj,
  api_key=OpenAIKey,
)


#NOTE if the code underneath this todaySummary is uncommented, comment this code below out

todaySummary = ouraPull.fetchAndOrganizeData()

#NOTE UNCOMMENT THE CODE UNDERNEATH AND ADD TEST DATA IF YOU WISH TO RUN THE CODE WITH TEST DATA
"""
todaySummary = {}
"""


today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
print("today: " + str(today))
todayIso = today.strftime("%Y-%m-%d")
yesterdayIso = yesterday.strftime("%Y-%m-%d")


print("todaysum: " + str(todaySummary))

#print(pd.json_normalize(todaySummary))

def saveHealthData(aiResp):
    try:
        with open('/home/harpbled/dataStorage/health/harper_health_data.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print("ERRORRR: ", e)

    print(f'data length: {len(data)}')
    if len(data) > 31:
        print('too many health dates')
        data.pop(0)  # This removes the first item in the list of health briefings
        print('removed the first item')


    healthData = {
        "date_of_data": yesterdayIso + " through " + todayIso,
        "date_of_data_pull": todayIso,
        "data": todaySummary,
        "AI_summary": aiResp,
    }
    data.append(healthData)

    print("Data: ", data)

    with open('/home/harpbled/dataStorage/health/harper_health_data.json', 'w') as f:
        json.dump(data, f, indent=2)


with open("/home/harpbled/dataStorage/health/how_to_analyze_oura_data.json") as f:
    howToRead = str(json.load(f))

print("Pending openai...")

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0,
    messages=[
        {"role": "system", "content": """
         You are a robot that compiles health data from the Oura Smart Ring and returns a summary in the format: NEGATIVE/POSITIVE: SUMMARY_OF_DIAGNOSIS; \ n POSSIBLE-TREATMENTS: POSSIBLE_TREATMENTS
         of the data inside it. A score mentioned should be positive unless it is under 70. WRITE POSITIVE OR NEGATIVE based on the health data by analyzing what would be healthy for the person with the personal data given. - if it is not very good, put negative, otherwise, put positive. 
        As a good rule of thumb, assume the data is positive. Your response should only be negative if a majority of the data is not good (BUT! if there are some potential bad issues such as an abnormally low SpO2 for the age of the user or high resting heart rate for their age, make the spo2 and heart rate exceptions).
         explain what some of the data could mean. Do not talk about the step count at all. Replace POSSIBLE_TREATMENTS with medicines that are reecommended to take for the symptoms shown (such as seeing the doctor, taking tylenol, naproxin sodium, etc)"""},
         {
             "role": "system",
             "content": "Here is a file that tells you how to read Oura Ring data. Before making your analysis, use this to be able to understand the health data. File: " + howToRead
         },
        {
            "role": "user",
            "content": str(todaySummary)
        }
    ]
)


resp = completion.choices[0].message.content

#saves health data to file
saveHealthData(resp)

#respSplit = resp.split()

#print(respSplit[0])

#if respSplit[0] == "NEGATIVE:":
#    print('negresp')
#    negative_section = resp.split("NEGATIVE:")[1].split("POSSIBLE-TREATMENTS:")[0].strip()
#    possible_treatments = resp.split("POSSIBLE-TREATMENTS:")[1].strip()
##    print('negative response: ', negative_section)
#    print('\n')
#    print('treatments: ', possible_treatments)

#    a.alfredBot.getChatbotResp("This is Harper\'s most recent health report. Do not run any functions. This is a compiled paragraph of the most recent symptoms. Please let her know of the symptoms and possible treatments made DO NOT mention any positives to her data; make it clear and concise with the negative. DATA: " + str(negative_section) + "; TREATMENTS: " + str(possible_treatments), sendPushNotification=True, customTokens=300)

#else:
#    print(respSplit[0])
#    print("not negative")



#print('\n')
#print(resp)
#print(respSplit)