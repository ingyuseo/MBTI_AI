#selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
#beautiful soup
from bs4 import BeautifulSoup

import time
import pandas as pd
import random
from typing import Dict
import re
import sys


def make_song_list(driver, mbti, count, num_per_person, data_list):
    start = 1
    if mbti == "ENFP" or mbti == "INTP" :# skip the first INTP, ENFP playlist (bad data)
        start +=1
        count +=1

    if mbti == "ISFP": 
        count += 1
    
    for i in range(start,count+1):
        driver.get(f'https://open.spotify.com/search/{mbti}/playlists')
        driver.implicitly_wait(5)
        
        if mbti == "ISFP" and i == 11:
            continue
        
        xpath = f'//*[@id="searchPage"]/div/div/div/div[1]/div[{i}]'
        playlist_box = driver.find_element(By.XPATH, xpath)
        playlist_box.click()
        time.sleep(2) # Data changes with no reason. so wait 2 seconds after page loading.
        
        print(mbti, i)

        #Get total number of songs in play list
        try:
            element = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/div/div[2]/main/div[1]/section/div[1]/div[5]/div/span[2]') # if like exists
        except:
            element = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/div/div[2]/main/div[1]/section/div[1]/div[5]/div/span')
            
        total_song_num = int(re.findall(r'\d+', element.text.replace(',',''))[0])
        n = total_song_num
        
        print(total_song_num)

        # Pick random number
        numbers_list = list(range(1, n + 1))
        selected_numbers = random.sample(numbers_list, k=min(num_per_person, n))
        
        # 스크롤 높이 가져옴
        itemlist = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div') # attribute에 scroll 이 있는 element 를 선택해야됬다...
        total_height = int(itemlist.get_attribute('scrollHeight'))   
        
        
        #Get song info
        for num in selected_numbers:
            SCROLL_PAUSE_SEC = 5
            
            height = (total_height*num)//total_song_num
            try:                     
                driver.execute_script(f"arguments[0].scrollTo(0, {height})", itemlist)
                row = WebDriverWait(driver, SCROLL_PAUSE_SEC).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@aria-rowindex={num+1}]"))
                )
                elem =row.find_element(By.XPATH, ".//div[@aria-colindex='2']")
                lines = elem.text.split('\n')  
                print(f'{num} song: {lines[0]}, singer:{lines[1]}')
                new_row = {'mbti': mbti, 'song': lines[0], 'singer': lines[1]}
                new_data = pd.DataFrame([new_row])
                data_list = pd.concat([data_list, new_data], ignore_index=False)
                
            except Exception as ex:
                print(ex)
                print(num)
                sys.exit() 
         
    return data_list
                

if __name__ == '__main__':

# WebDriver 생성
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    mbti_list = ["ESFP"]

#done INTP ISTP "ISFP ISFJ INFJ "INTJ",  "ENFP", "ENTP", 
#todo   "ESTJ", "ESFJ", "ENFJ","ISTJ","ENTJ", "INFP","ESTP", "ESFP", 
  
    
    num_people = 25
    song_per_person = 4
    
    mbti_song_data = pd.read_csv('mbti_data.csv')
    #mbti_song_data = pd.DataFrame(columns=['mbti', 'song', 'singer'])
    
    for mbti in mbti_list:
        mbti_song_data = make_song_list(driver, mbti, num_people, song_per_person, mbti_song_data)
        print(mbti_song_data.shape[0])
        mbti_song_data.to_csv('mbti_data.csv', index=False)

        
