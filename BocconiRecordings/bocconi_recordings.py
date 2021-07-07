# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import requests
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def read_credentials(file_name):
    '''Takes as an input a file name, which should be formatted as JSON'''
    
    if file_name[-5:] != '.json':
        raise Exception('Must provide a .json file')
    
    with open(file_name, 'r') as f:
        data = json.load(f)
    
    return data['ID'], data['PW'], data['COURSE_ID']

def download_lecture():
    
    
    #Initializes a chrome webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    
    #Goes to the bocconi website
    driver.get('https://blackboard.unibocconi.it/')
    
    #Reads in the ID and PW of the account out of a credentials folder
    bocconi_id, bocconi_pw, course_id = read_credentials('credentials.json')
    
    #Finds field username and sends the username keys
    id_matricola_field = driver.find_element_by_xpath('//input[@id="username"]')
    id_matricola_field.send_keys(bocconi_id)
    
    #Finds field password and sends the password keys
    password_matricola = driver.find_element_by_xpath('//input[@id="password"]')
    password_matricola.send_keys(bocconi_pw + Keys.RETURN)
    
    #Implicitly waits a couple of secs for it to load
    driver.implicitly_wait(2)
    
    #Gets the selected course url and follows the path
    course_url = driver.find_element_by_xpath(f'//div[@class="courseList"]/a[ contains(text(), {course_id}) and not(contains(text(), "EXAM")) ]')
    course_url.click()
    
    #Gets the live room for the selected course
    live_room = driver.find_element_by_xpath('//a[span[.="Live Room"]]')
    live_room.click()
        
    #Gets src from iframe, since the iframe interface is just a forwarding of another page
    src = driver.find_element_by_xpath('//iframe[@id="collabUltraLtiFrame"]').get_attribute('src')
    
    #Opening a new tab and getting that iFrame to open up
    driver.execute_script(f'window.open("{src}","_blank");')
    
    #Switching controls to that other page
    driver.switch_to.window(driver.window_handles[1])
    
    #Setting an explicit time wait for the element to load, max 15 secs
    wait = WebDriverWait(driver, 15)
    
    wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@id='side-menu-toggle']")))
    
    #Toggles the menu, since we need to select the dates in which lectures are uploaded
    driver.find_element_by_xpath("//button[@id='side-menu-toggle']").click()
    
    driver.find_element_by_xpath('//a[contains(href , recording) and @ui-sref = "recording.base"]').click()
    
    driver.find_element_by_xpath('//button[contains(id, filter-toggle) and @aria-haspopup="true"]').click()
    
    driver.find_element_by_xpath('//button[contains(id, select-range) and @role="option" and @data-index="1"]').click()
    
    #Starting from today's date gets one day ago and one day in the future
    start_date_field, end_date_field = driver.find_elements_by_xpath('//input')[:2]
    
    today = datetime.today()
    two_ago = today - timedelta(days=1)
    two_next = today + timedelta(days=1)
    
    #Clears the field of start and end date
    start_date_field.clear()
    end_date_field.clear()
    
    #Stringyfies the dates for which to search and inserts them on the page
    start_date_field.send_keys(two_ago.strftime('%m/%d/%y'))
    driver.implicitly_wait(1)
    end_date_field.send_keys(two_next.strftime('%m/%d/%y'))
    
    #Clicks somewhere else, because otherwise the scroll down menues above remain open
    driver.find_element_by_xpath('//div[@id="body-content"]').click()
    
    driver.implicitly_wait(2)
    
    #Gets all the recordings
    recordings = driver.find_elements_by_xpath('//td[@class="break-word content-table__emphasis"]/button[contains(id, recording)]')
    
    #Not get all recordings and check which one are already in the database
    times = [t.text for t in driver.find_elements_by_xpath('//span[@class="date"]/span')]
    
    #Zipping each unique recording time to the file, this is going to be the file name later on for storage
    times_elems = list(zip(times,recordings))
    
    for time_elem in times_elems:
    
        time_elem[1].click()
        
        #Goes to the recording page, opening another tab
        driver.find_element_by_xpath('//button[@class="button preserve focus-item loading-button"]').click()
        
        driver.switch_to.window(driver.window_handles[-1])
        
        #Waits until element is visible to get the source url of the recording
        url_download_video = wait.until(EC.visibility_of_element_located((By.XPATH, "//video"))).get_attribute('src')
        
        #Stores the current cookies of the browser and sends with those a request to the same endpoint to get the video respoonse
        cookies = driver.get_cookies()
        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
        response = s.get(url_download_video, stream=True)
        print('Status code:', response.status_code)
        
        #Since the video response comes in a bytes form, we need to write bytes to an mp4 file locally
        print('Downloading the lecture...')
        with open(f'{course_id} - {time_elem[0].replace("/","_")}.mp4', 'wb+') as wfile:
            wfile.write(response.content)
        print('Download complete.')
        
        #Switches back to the other page and keeps on downloading the other lectures
        driver.implicitly_wait(1)
        driver.switch_to.window(driver.window_handles[-2])
        driver.implicitly_wait(1)
        
    
        #Insert code here if you want to store your stuff inside the google drive
        #A bit messier, you need to get google APIs tokens from the web and insert them
        #Then create a folder, retrieve its ID and put it in the file googledrive.py
        
        #google_auth = GoogleAuthentication()
        #google_auth.list_files_in_root()
        #google_auth.create_file(f'{course_id} - {time_elem[0].replace("/","_")}.mp4')
    
    
    #driver.quit()
    
if '__main__'==__name__:
    download_lecture()
    
    
    
    