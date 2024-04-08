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

# ChromeOptions를 생성하여 다운로드 디렉토리를 설정합니다.
chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    'download.default_directory': download_directory,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True
})

driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

song_list = pd.read_csv("mbti_data.csv")

todo = 0

for index, row in enumerate(song_list.iloc[todo:].itertuples(index=False), start=todo):
    
    new_file_name = f'{row.song}_{row.singer}.mp3'
    invalid_chars = re.compile(r'[\\/:"*?<>|]+')
    new_file_name = re.sub(invalid_chars, '', new_file_name)
    new_file_path = os.path.join(download_directory,  row.mbti ,new_file_name)
    
    
    if os.path.exists(new_file_path):
        continue
    
    print(f'{index}, {row.song} - {row.singer}  ({row.mbti})')
    
    search_query = quote(f"{row.song} {row.singer}")
    url = f'https://www.youtube.com/results?search_query={search_query}'
    driver.get(url)
    driver.implicitly_wait(5)
    
    video_link = driver.find_element(By.CSS_SELECTOR,'a#video-title')
    video_link = video_link.get_attribute("href")
    
    while True:
        driver.get(f'https://ko.onlymp3.to/')
        input_element = driver.find_element(By.ID,"txtUrl")
        input_element.send_keys(video_link)
        time.sleep(1)
        
        button = driver.find_element(By.ID, "btnSubmit")
        button.click()
        
        try:
            btn = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".btn a"))
            )
            btn.click() #이 버튼 클릭시 다운로드
            time.sleep(1)
            break
        except Exception as ex:
            time.sleep(60)
        
    current_handle = driver.current_window_handle
    new_handle = driver.window_handles[1]
    
    driver.switch_to.window(new_handle)
    driver.close()
    driver.switch_to.window(current_handle)
      
    while True:
        files = glob.glob(download_directory+"\*.*")  # 현재 디렉토리의 모든 파일 목록을 가져옴
        downloaded_file = files[0]
        
        if downloaded_file.endswith('.mp3'):
            old_file_path = os.path.join(download_directory, downloaded_file) 
            shutil.move(old_file_path, new_file_path)
            break 
        else:
            time.sleep(3)
    
    
        
        
        
        



    