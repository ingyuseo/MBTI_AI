#selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

#beautiful soup
from bs4 import BeautifulSoup

import time
import pandas as pd
import random
from typing import Dict
import re


def make_song_list(driver, mbti, count, num_per_person) -> Dict[str, str]:
    
    for i in range(1,count+1):
        driver.get(f'https://open.spotify.com/search/{mbti}/playlists')
        driver.implicitly_wait(3)
        
        xpath = f'//*[@id="searchPage"]/div/div/div/div[1]/div[{i}]'
        playlist_box = driver.find_element(By.XPATH, xpath)
        playlist_box.click()

        driver.implicitly_wait(3)
        element = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/div/div[2]/main/div[1]/section/div[1]/div[5]/div/span[2]')
        text_content = element.text
        
        #Get total number of songs in play list
        total_song_num = int(re.findall(r'\d+', text_content)[0])   
        n = total_song_num

        # Pick random number
        numbers_list = list(range(1, n + 1))
        selected_numbers = random.sample(numbers_list, k=min(num_per_person, n))  
        
        #Get song info
        for num in selected_numbers:   
            SCROLL_PAUSE_SEC = 0.2

            # 스크롤 높이 가져옴
            itemlist = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div') # attribute에 scroll 이 있는 element 를 선택해야됬다...
            scroll_height = int(itemlist.get_attribute('scrollHeight'))
            height = (scroll_height*num)//total_song_num

            try:                     
                driver.execute_script(f"arguments[0].scrollTo(0, {height})", itemlist)
                time.sleep(SCROLL_PAUSE_SEC)
                elem = driver.find_element(By.XPATH, f"//div[@aria-rowindex={num+1}]")
                
            except Exception as ex:
                print('Maybe, can not find song element', ex)
                
            

if __name__ == '__main__':
    driver = webdriver.Chrome() 
    driver.maximize_window()
    
    mbti_list = [ "INTP", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP","ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]

    #except ISTJ, because there is a album named ISTJ. NCT DREAM.. 
    #ENFP also NCT DREAm..
    num_people = 25
    song_per_person = 8
    mbti_song_data = pd.DataFrame(columns=['mbti', 'song', 'writer'])
    
    for mbti in mbti_list:
        song_list = make_song_list(driver, mbti, num_people, song_per_person)
        song_list['mbti'] = [mbti] * len(num_people*song_per_person)
        mbti_song_data = mbti_song_data.append(song_list, ignore_index = True)
    
    mbti_song_data.to_csv('mbti_data.csv', index=True)
        
        
