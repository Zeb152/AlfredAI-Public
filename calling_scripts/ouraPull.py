import requests
import datetime
import os
import sys
sys.path.insert(1, '/home/harpbled')
import loadApiKeys

api_token = os.getenv("OURA_API_KEY")

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
todayIso = today.strftime("%Y-%m-%d")
yesterdayIso = yesterday.strftime("%Y-%m-%d")

def get_oura_data(history_type):
    url = f'https://api.ouraring.com/v2/usercollection/{history_type}'
    headers = {
        "Authorization": f"Bearer {api_token}"
        }
    params={ 
    'start_date': yesterdayIso, 
    'end_date': todayIso 
    }
    #response = requests.get(url, headers=headers)
    response = requests.request('GET', url, headers=headers, params=params)

    if response.status_code == 200: 
        #print(response.text)
        return response.json()
    else:
        print("Error:", response.text)


def fetchAndOrganizeData():

    #PERSONAL INFO
    userPersonalData = get_oura_data("personal_info")
    age = "AGE: " + str(userPersonalData["age"]) + " YEARS"
    height = "HEIGHT: " + str(userPersonalData["height"]) + "M"
    weight = "WEIGHT: " + str(userPersonalData["weight"]) + "KG"
    print(f"PERSONAL INFO -> AGE: {age}, HEIGHT: {height}, WEIGHT: {weight}")

    #DAILY READINESS
    readinessData = get_oura_data("daily_readiness")
    print("Readiness score:", readinessData["data"][0]["score"])
    print("Likely contributions to score: ", readinessData["data"][0]["contributors"])
    yesReadinessScore = str(readinessData["data"][0]["score"])
    yesContribReadiness = "Contributions to readiness score: " + str(readinessData["data"][0]["contributors"])

    todReadinessScore = str(readinessData["data"][1]["score"])
    todContribReadiness = "Contributions to today readiness score: " + str(readinessData["data"][1]["contributors"])

    #DAILY SLEEP
    sleepData = get_oura_data("daily_sleep")
    print("Sleep score:", sleepData["data"][0]["score"])
    print("Likely contributions to score: ", sleepData["data"][0]["contributors"])
    yesSleepScore = str(sleepData["data"][0]["score"])
    yesContribSleep = "Contributions to sleep score: " + str(sleepData["data"][0]["contributors"])

    todSleepScore = str(sleepData["data"][1]["score"])
    todContribSleep = "Contributions to sleep score: " + str(sleepData["data"][1]["contributors"])

    #DAILY ACTIVITY
    activityData = get_oura_data("daily_activity")
    print("activity score:", activityData["data"][0]["score"])
    print("Activity data: ", activityData["data"][0])
    yesActivityScore = str(activityData["data"][0]["score"])
    yesActivityMeasurements = str(activityData["data"][0])
    #todActivityScore = str(activityData["data"][1]["score"])
    #todActivityMeasurements = str(activityData["data"][1])

    #workoutData = get_oura_data("workout")
    #print("WORKOUT DATA: ", workoutData)

    #heartRateData = get_oura_data("heartrate")
    #print("HEART: ", heartRateData)

    #DAILY SPO2
    spoData = get_oura_data("daily_spo2")
    print("SpO2 Percentage: ", spoData["data"][0]["spo2_percentage"])
    yesSpoPercentage = str(spoData["data"][0]["spo2_percentage"]["average"])
    todSpoPercentage = str(spoData["data"][1]["spo2_percentage"]["average"])

    #DAILY STRESS
    stressData = get_oura_data("daily_stress")
    print("Stress data: ", stressData["data"][0])
    yesStressMeasurements = str(stressData["data"][0])
    todStressMeasurements = str(stressData["data"][1])

    #NOTE Resilience returns no data. I think it is due to lack of time the ring has been worn
    #resilienceData = get_oura_data("daily_resilience")
    #print("Resilience level: ", resilienceData["data"][0]["level"])
    #print("Likely contributions to resilience: ", resilienceData["data"][0]["contributors"])


    healthReport = {
        "User": "Harper Bledsoe",
        "Personal info": [
            age,
            height,
            weight
        ],
        "health_data": [
            {
                "today_data": [
                    {
                        "readiness_data": {
                            "readiness_score": todReadinessScore,
                            "contributions_to_score": todContribReadiness
                        }
                    },
                    {
                        "sleep_data": {
                            "sleep_score": todSleepScore,
                            "contributions_to_score": todContribSleep
                        }
                    },
                    {
                        "average_spo2_percentage": todSpoPercentage
                    }
                ],
                "yesterday_data": [
                    {
                        "activity_data": {
                            "activity_score": yesActivityScore,
                            "contributions_to_score": yesActivityMeasurements
                        }
                    },
                    {
                        "stress_data": yesStressMeasurements
                    }
                ]
            }
        ]
    }

    return healthReport

#For testing
#print(fetchAndOrganizeData())