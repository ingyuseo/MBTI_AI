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


def make_song_list(driver, mbti, count, num_per_person, data_list):
    start = 1
    if mbti == "ENFP" or "INTP" : # skip the first INTP, ENFP playlist (bad data)
        start +=1
        count +=1

    for i in range(start,count+1):
        driver.get(f'https://open.spotify.com/search/{mbti}/playlists')
        driver.implicitly_wait(5)
        
        xpath = f'//*[@id="searchPage"]/div/div/div/div[1]/div[{i}]'
        playlist_box = driver.find_element(By.XPATH, xpath)
        playlist_box.click()
        time.sleep(1) # Data changes with no reason. so wait 2 seconds after page loading.
        
        print(mbti, i)

        #Get total number of songs in play list
        try:
            element = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/div/div[2]/main/div[1]/section/div[1]/div[5]/div/span[2]') # if like exists
        except:
            element = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/div/div[2]/main/div[1]/section/div[1]/div[5]/div/span')
            
        total_song_num = int(re.findall(r'\d+', element.text.replace(',',''))[0])
        n = total_song_num

        # Pick random number
        numbers_list = list(range(1, n + 1))
        selected_numbers = random.sample(numbers_list, k=min(num_per_person, n))   
        
        #Get song info
        for num in selected_numbers:
            SCROLL_PAUSE_SEC = 5
            
            # 스크롤 높이 가져옴
            itemlist = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div') # attribute에 scroll 이 있는 element 를 선택해야됬다...
            total_height = int(itemlist.get_attribute('scrollHeight'))
            height = (total_height*num)//total_song_num
            
            try:                     
                driver.execute_script(f"arguments[0].scrollTo(0, {height})", itemlist)
                elem = WebDriverWait(driver, SCROLL_PAUSE_SEC).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@aria-rowindex={num+1}]"))
                )
                lines = elem.text.split('\n')
                print(num , lines[1], lines[2])
                new_row = {'mbti': mbti, 'song': lines[1], 'singer': lines[2]}
                data_list.loc[len(data_list)] = new_row
                
            except Exception as ex:
                print('!!!!!!!Can not find song element!!!!!!!!!', num)
                return False
            
    return True
                


if __name__ == '__main__':
    driver = webdriver.Chrome() 
    driver.maximize_window()
    
    mbti_list = [ "INTP", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP","ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    #except ISTJ, because there is a album named ISTJ. NCT DREAM.. 
    #ENFP also NCT DREAm..
    
    num_people = 25
    song_per_person = 8
    mbti_song_data = pd.DataFrame(columns=['mbti', 'song', 'singer'])
    
    for mbti in mbti_list:
        if make_song_list(driver, mbti, num_people, song_per_person, mbti_song_data) == False:
            break
        mbti_song_data.to_csv('mbti_data.csv', index=True)
        
    print('done!')
        
