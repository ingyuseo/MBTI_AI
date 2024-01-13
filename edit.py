#selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote

#beautiful soup
from bs4 import BeautifulSoup

import time
import pandas as pd
import random
from typing import Dict
import os
import glob
import re
import shutil

download_directory = r'C:\Users\82103\Desktop\4-1학기\졸작\MBTI_Music\songs'

song_list = pd.read_csv("mbti_data.csv")

todo = 0

lists = ["INTP", "ISTP", "ISFP", "ISFJ", "INFJ", "INTJ", "ENFP", "ENTP",  "ESTJ", "ESFJ", "ENFJ","ISTJ","ENTJ", "INFP","ESTP", "ESFP"]
exist = {}

personality_types = ["INTP", "ISTP", "ISFP", "ISFJ", "INFJ", "INTJ", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ISTJ", "ENTJ", "INFP", "ESTP", "ESFP"]
personality_dict = {ptype: [] for ptype in personality_types}

for mbti in lists:
    exist[mbti] = os.listdir(os.path.join(download_directory,mbti))

for index, row in enumerate(song_list.iloc[todo:].itertuples(index=False), start=todo):
    new_file_name = f'{row.song}_{row.singer}.mp3'
    invalid_chars = re.compile(r'[\\/:"*?<>|]+')
    new_file_name = re.sub(invalid_chars, '', new_file_name)
    new_file_path = os.path.join(download_directory,  row.mbti ,new_file_name)
    
    personality_dict[row.mbti].append(new_file_name)
    
for mbti in lists:
    unique_elements = list(set(exist[mbti]) ^ set(personality_dict[mbti]))
    for song in unique_elements:
        os.remove(os.path.join(download_directory, mbti, song))
    
    