"""\
                            get_ovo_data.py

This is the only way I found to automate everything after the login. Based on:

https://stackoverflow.com/questions/37121843/\
how-to-get-a-json-response-from-a-google-chrome-selenium-webdriver-client

Simon Duane
2021-10-10
"""

from datetime import datetime, timedelta
import json
import os
from random import random
from time import sleep
from selenium import webdriver          # read for yourself how to use selenium

# if you have multiple accounts with ovo, give them pet names
accounts = ['my_pet_name']              # make up arbitrary name(s) here
ac_dict = {'my_pet_name': 1234567}      # insert ovo account number(s) here
json_root = "./json/"                   # data files will be written here
earliest = "2022-01-01"                 # yyyy-mm-dd: THE EARLIEST DATA READ

for ac in accounts:
    for folder in ["/daily", "/half-hourly"]:
        try:
            os.listdir(json_root + ac + folder)
        except FileNotFoundError:
            print("""
SAFETY FIRST: this script expects you to have already made the directories
""")
            raise

driver = webdriver.Firefox()
driver.get("https://my.ovoenergy.com/login") # login manually and accept cookies
input(f"""If needed: select account in the browser then click continue there ...
... then press Return here: """)

for ac in accounts:
    account_id = ac_dict[ac]
    yesterday = (datetime.now() - timedelta(days=1)).date()     # Ovo's most ...
    dt = datetime(yesterday.year, yesterday.month, 1)           #... recent data
    year = dt.year                      # year and month are used together ...
    month = dt.month                    #... as the loop counter
    file = f"{year}-{month:02d}"        # read files, starting at yesterday, ...
    while file >= earliest[:7]:         #... month by month, back to "yyyy-mm"
################################################################################
        print(f"Loading daily data for {ac}, {file} ...")
################################################################################
        driver.get(f"view-source:https://smartpaym.ovoenergy.com/" +
                   f"api/energy-usage/daily/{account_id}?date={file}")
        pre = driver.find_element_by_tag_name("pre").text
        if ('Error' in pre or '"electricity":null' in pre):
            print(f"... no daily data for {file}")
            break
        with open(json_root + f"{ac}/daily/{file}.json",'w') as json_file:
            print(f"saving json data for {file}...")
            json_file.write(pre)
        month -= 1                      # there are trickier ways to do this ...
        if month == 0:                  # but I like my code to be easy to read
            month = 12                  #... and ...
            year -= 1                   #... easy to understand
        file = f"{year}-{month:02d}"    # the loop counter
        sleep(1+2*random())             # this is polite (but not needed?)

    dt = datetime(yesterday.year, yesterday.month, yesterday.day)
    file = f"{dt.year}-{dt.month:02d}-{dt.day:02d}"   # NB dt hasn't changed yet
    while file >= earliest:              # read files back to yyyy-mm-dd
################################################################################
        print(f"Loading half-hourly data for {ac}, {file} ...")
################################################################################
        driver.get(f"view-source:https://smartpaym.ovoenergy.com/" +
                   f"api/energy-usage/half-hourly/{account_id}?date={file}")
        pre = driver.find_element_by_tag_name("pre").text
        if 'Error' in pre or '"electricity":null' in pre:
            print(f"... no half-hourly data for {file}")
            break
        with open(f"./json/{ac}/half-hourly/{file}.json",'w') as json_file:
            print(f"saving json data for {file}...")
            json_file.write(pre)
        dt -= timedelta(days=1)
        file = f"{dt.year}-{dt.month:02d}-{dt.day:02d}"      # the loop variable
        sleep(1+2*random())
driver.get("https://my.ovoenergy.com/login")
print("Downloading of data has now finished - please log out.")
