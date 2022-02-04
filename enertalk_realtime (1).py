# authentication ##
# 2021-03-05
# https://developer.enertalk.com/authentication/
# ID: ibk1930@gmail.com
# ID: 01043376988
# PW: Sed05062!@

# 2021-03-19
# ���� �ʹ� ���ؼ� ������ ������ ����


from time import sleep
import requests
import schedule
import json
import os
import os.path
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
import schedule
import time


def getCode():
    URL = "https://auth.enertalk.com/authorization"
    headers = {"Content-Type": "application/json"}
    params = {
        "client_id": "aWJrMTkzMEBnbWFpbC5jb21fYTU3Mg==",
        "response_type": "code",
        "redirect_uri": "http://localhost:8080/callback"
    }
    response = requests.get(URL, headers=headers, params=params)
    driver = webdriver.Chrome(r'/usr/local/bin/chromedriver')
    driver.get(response.url)
    driver.find_element_by_xpath("/html/body/article/section/div[2]/div[2]").click()
    driver.find_element_by_xpath("/html/body/article/section/div[3]/form/div[1]/div[1]/input").send_keys('01043376988')
    driver.find_element_by_xpath("/html/body/article/section/div[3]/form/div[1]/div[2]/input").send_keys('Sed05062!@')
    driver.find_element_by_xpath("/html/body/article/section/div[3]/form/div[2]/input[1]").click()
    received_code = driver.current_url.split('code=')[-1]
    driver.quit()
    print('{}\ncode: {}\n{}\n'.format('*'*40,received_code,'*'*40))
    return received_code
#!url에서 아이디로 code 받기
#!chrome driver 공부

def getAccessToken(code):
    URL =  "https://auth.enertalk.com/token"
    headers = {"Content-Type": "application/json"}
    pload = {
        "client_id": "aWJrMTkzMEBnbWFpbC5jb21fYTU3Mg==",
        "client_secret": "3u1bg6ay1qq4un96z2p59w14al5cf5hk7q04s25",
        "grant_type": "authorization_code",
        "code" :code
    }
    response = requests.post(URL, headers=headers, data=json.dumps(pload))
    response_native = json.loads(response.text)
    print(response)
    print(response_native)    
    return response_native['access_token']



#!token 받기

def getRealTimeUsage(ACCESS_TOKEN,before_time=15):
    dt_from  = datetime.now()-timedelta(hours=9)-timedelta(minutes=before_time)
    dt_to    = datetime.now()-timedelta(hours=9)
    utc_from = int((dt_from-datetime(1970,1,1)).total_seconds()*1000)
    utc_to   = int((dt_to  -datetime(1970,1,1)).total_seconds()*1000)

    URL = f"https://api2.enertalk.com/devices/1f94d900/usages/periodic/?start={utc_from}&end={utc_to}"
    headers = {"Authorization" : f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(URL, headers= headers)
    response_native = json.loads(response.text)

    dt_start_real = datetime.fromtimestamp(response_native['start']/1000)
    dt_end_real   = datetime.fromtimestamp(response_native['end']/1000)

    print(dt_start_real.strftime('%Y-%m-%d %H:%M:%S'))
    print(dt_end_real.strftime('%Y-%m-%d %H:%M:%S'))
    print(f'usage: {response_native["usage"]} Wh')
    return dt_start_real, dt_end_real, response_native['usage']

def getRealTimePower(ACCESS_TOKEN):

    URL = f"https://api2.enertalk.com/devices/1f94d900/usages/realtime"
    headers = {"Authorization" : f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(URL, headers= headers)
    sleep(0.8)
    response = requests.get(URL, headers= headers)
    response_native = json.loads(response.text)
    Duration    = response_native['timestampDiff']/1000
    activePower = response_native['activePower']/1000
    print(datetime.fromtimestamp(response_native['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S'))
    print(f"activePower: {activePower} W")
    return activePower

def makeFile(name):
    if not os.path.isfile('{}'.format(name)):
        file = open('{}'.format(name),'a')
        headers = ['','ref time','time','usage']
        for header in headers:
            file.write(header+',')
        file.write('\n')
        file.close()
        

    

def toCSVRealTimePower():
    now = datetime.now().strftime('%d-%B-%Y %H')
    if not os.path.isfile('save/{} enertalk_realtime_power.csv'.format(now)):
        makeFile('save/{} enertalk_realtime_power.csv'.format(now))
    df = pd.read_csv('save/{} enertalk_realtime_power.csv'.format(now), index_col=0)
    time = datetime.now().strftime('%Y-%m-%d T%H:%M:%SZ')
    power = getRealTimePower(ACCESS_TOKEN=ACCESS_TOKEN)
    df = df.append({'time':time, 'power': power}, ignore_index=True)
    df.to_csv('save/{} enertalk_realtime_power.csv'.format(now))

def toCSVRealTimeUsage():
    now = datetime.now().strftime('%d-%B-%Y %H')
    if not os.path.isfile('save/{} enertalk_realtime_usage.csv'.format(now)):
        makeFile('save/{} enertalk_realtime_usage.csv'.format(now))
    df = pd.read_csv('save/{} enertalk_realtime_usage.csv'.format(now), index_col=0)
    start_time, end_time, usage = getRealTimeUsage(ACCESS_TOKEN=ACCESS_TOKEN)
    if len(df) > 0:
        if datetime.strptime(df.loc[len(df)-1, 'time'],'%Y-%m-%d T%H:%M:%SZ') > end_time:
            end_time += timedelta(seconds=30)
    start_time = start_time.strftime('%Y-%m-%d T%H:%M:%SZ')
    end_time   = end_time.strftime('%Y-%m-%d T%H:%M:%SZ')

    df = df.append({'ref time':start_time, 'time': end_time, 'usage': usage}, ignore_index=True)
    df.to_csv('save/{} enertalk_realtime_usage.csv'.format(now))

def updateToken():
	global ACCESS_TOKEN
	received_code = getCode()
	ACCESS_TOKEN = getAccessToken(received_code)

updateToken()
schedule.every(60*60).seconds.do(updateToken)
schedule.every(10).seconds.do(toCSVRealTimeUsage)
while True:
    schedule.run_pending()
    sleep(5)
