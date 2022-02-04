# authentication ##
# 2022-01-26
# https://developer.enertalk.com/authentication/
# ID: ibk1930@gmail.com
# ID: 01043376988
# PW: Sed050762!@

from time import sleep
import requests
import json
import os
import os.path
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
import schedule
import time

def getCode():
    url = "https://auth.enertalk.com/authorization?client_id=aWJrMTkzMEBnbWFpbC5jb21fYTU3Mg==&response_type=code&redirect_uri=http://localhost:8080/callback"

    payload={
        "client_id": "aWJrMTkzMEBnbWFpbC5jb21fYTU3Mg==",
        "response_type": "code",
        "redirect_uri": "http://localhost:8080/callback"
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)

    driver = webdriver.Chrome(r"C:\Users\최희주\Documents\엄소은\vscode\chromedriver_win32\chromedriver.exe")
    driver.get(response.url)
    driver.find_element_by_xpath("/html/body/article/section/div[2]/div[2]").click()
    driver.find_element_by_xpath("/html/body/article/section/div[3]/form/div[1]/div[1]/input").send_keys('01043376988')
    driver.find_element_by_xpath("/html/body/article/section/div[3]/form/div[1]/div[2]/input").send_keys('Sed050762!@')
    driver.find_element_by_xpath("/html/body/article/section/div[3]/form/div[2]/input[1]").click()
    received_code = driver.current_url.split('code=')[-1]
    driver.quit()
    print('{}\ncode: {}\n{}\n'.format('*'*40,received_code,'*'*40))
    return received_code