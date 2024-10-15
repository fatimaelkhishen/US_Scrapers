import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time
import json
from json import JSONDecoder
import re


def get_job_links():  
    job_links = []  
    p = 1   
    driver = webdriver.Chrome()  

    try:  
        while True:  
            url = f"https://jooble.org/SearchResult?rgns=united%20states&page={p}"  
            print(f"Accessing page: {url}")    

            driver.get(url)  
            time.sleep(5)    

             
            try:  
                consent_button = WebDriverWait(driver, 10).until(  
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="cookiescript_accept"]'))  
                )  
                consent_button.click()  
                print("Cookie consent accepted.")  
                time.sleep(1)   
            except Exception as e:  
                print("No cookie consent button found or error occurred:", e)  

              
            try:  
                close_button = WebDriverWait(driver, 10).until(  
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[3]/div/div[1]/div[1]/button'))  
                )  
                close_button.click()  
                print("Close button clicked.")  
                time.sleep(1)    
            except Exception as e:  
                print("No close button found or error occurred:", e)  

            
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            
            page_source = driver.page_source
            print(page_source[:2000])  

            try:  
                job_cards = driver.find_elements(By.XPATH, '//*[@data-test-name="_jobCard"]')
                print(f"Found {len(job_cards)} job cards on page {p}.")   
            except Exception as e:  
                print("Job cards not found or error occurred:", e)  
                break  

            if not job_cards:  
                print("No job cards found on this page.")  
                break  
            
            for job_card in job_cards:  
                title_element = job_card.find_element(By.TAG_NAME, "h2")  
                if title_element:  
                    link = title_element.find_element(By.TAG_NAME, 'a').get_attribute('href')  
                    if link:  
                        job_links.append(link)  
                        print(f"Job link added: {link}")  
                else:  
                    print("Title not found in job card.")   
            
            p += 1   

    except Exception as e:  
        print("An error occurred:", e)  
    
    finally:  
        driver.quit()  
    return job_links


def construct_job(driver, job_link):
    driver.get(job_link)
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        title = soup.find('h2', class_='sXM9Eq PkepBU').text.strip()
    except:
        title = "NA"
    try:
        job_description = soup.find('div',class_='PAM72f').text.strip()
    except:
        job_description = "NA"
    try:
        type = soup.find("div", {"data-test-name": "_jobTag"}).text.strip()
    except:
        type = "NA"
    try:
       company = soup.find('div',class_='pXyhD4 VeoRvG').text.strip()
    except:
       company = "NA"
    try:
       location = soup.find('div',class_='caption NTRJBV').text.strip()
    except:
       location= "NA"
    try:
       date_posted = soup.find('div',class_='caption Vk-5Da').text.strip()
    except:
       date_posted= "NA"

    jobPosting = {
        'SRC_Title': title,
        'SRC_Company': company,
        'SRC_Country': location,
        'Posting_date': date_posted,
        'SRC_Type':type,
        'Job_Link': job_link,
        'SRC_Description': job_description,
        'Website': 'Jooble'
    }
    return jobPosting
    
 
def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Jooble.xlsx", index=False)

def main():
    job_links = get_job_links()
    driver = webdriver.Chrome()
    job_data = []
    for link in job_links:
        job_posting = construct_job(driver, link)
        job_data.append(job_posting)
    driver.quit()
    save_to_excel(job_data)

if __name__ == "__main__":
    main()