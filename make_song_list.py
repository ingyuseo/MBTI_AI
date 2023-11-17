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

def make_song_list(driver, mbti, count, num_per_person):
    
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
        total_song_num = text_content.split('곡')[0]              
        n = int(total_song_num)

        # Pick random number
        numbers_list = list(range(1, n + 1))
        selected_numbers = random.sample(numbers_list, k=min(num_per_person, n))
    
        selected_numbers = [300]
        
        #Get song info
        for num in selected_numbers:   
            SCROLL_PAUSE_SEC = 2

            # 스크롤 높이 가져옴
            itemlist = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div') # attribute에 scroll 이 있는 element 를 선택해야됬다...
            last_height = itemlist.get_attribute('scrollHeight') 
            
            while True:
                print(last_height)

                # 끝까지 스크롤 다운
                driver.execute_script(f"arguments[0].scrollBy(0, {last_height})", itemlist)
                time.sleep(SCROLL_PAUSE_SEC)

                # 스크롤 다운 후 스크롤 높이 다시 가져옴
                new_height = itemlist.get_attribute('scrollHeight') 
                if new_height == last_height:
                    break
                last_height = new_height
            
            xpath = f'//*[@id="main"]/div/div[2]/div[3]/div[1]/div[2]/div[2]/div/div/div[2]/main/div[1]/section/div[2]/div[3]/div/div[2]/div[2]/div[{num}]'
            elem = driver.find_element(By.XPATH, f"//div[@aria-rowindex={num+1}]")
            print(elem.text)


if __name__ == '__main__':
    driver = webdriver.Chrome() 
    driver.maximize_window()
    
    mbti_list = ["ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]

    #except ISTJ, because there is a album named ISTJ. 
    
    for mbti in mbti_list:
        make_song_list(driver, mbti, 25, 8)
        
