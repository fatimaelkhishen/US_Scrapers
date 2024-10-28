import pandas as pd  
from bs4 import BeautifulSoup  
from selenium import webdriver  
import re
import time  
import json
import random  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  

def get_job_links():  
    job_links = []  
    driver = webdriver.Chrome()   
    driver.get("https://www.diversityjobboard.com/jobs")  
    time.sleep(5)   
    base_url = "https://www.diversityjobboard.com"  
    page_number = 1  

    try:  
        while True:  
            WebDriverWait(driver, 30).until(  
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-listings-item"))  
            )  
            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all("div", class_="job-listings-item")  

            if not listings:  
                break  

            for listing in listings:  
                try:  
                    job_link = listing.find("a")['href']  
                    if job_link:  
                        if job_link.startswith('/'):  
                            job_link = base_url + job_link  
                        job_links.append((job_link, page_number))    
                except Exception:  
                    pass  

            try:   
                next_button = WebDriverWait(driver, 10).until(  
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']"))  
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_button)  
                next_button.click()   
                time.sleep(random.uniform(2, 5))   
                page_number += 1  

            except Exception:  
                print("No more 'Next' button found or unable to click. Exiting.")
                break  

    finally:  
        driver.quit()  

    return job_links  

def construct_job(driver, job_link_page):  
    job_link, _ = job_link_page  

    if not job_link or not job_link.startswith(('http://', 'https://')):  
        return None    

    driver.get(job_link)  
    
    
    try:
        WebDriverWait(driver, 40).until(  
            EC.presence_of_element_located((By.CLASS_NAME, "jb-text-size-3xl"))
        )  
    except Exception:
        print(f"Timeout waiting for job details on page: {job_link}")
        return None
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')  
    
    
    try:  
        title = soup.find("h1", class_="jb-text-size-3xl").text.strip() 
    except Exception:  
        title = 'NA'  

   
    try:  
        description = soup.find(id='quill-container-with-job-details').text.replace('\n', '').strip()    
    except Exception:  
        description = 'NA' 

    
    try:
        detail_box = soup.find("div", class_="job-inner-detail-box")
        info_items = detail_box.find_all("a", class_="d-inline-block")

       
        Company = info_items[0].text.strip() if len(info_items) > 0 else 'NA'
        job_type = info_items[1].text.strip() if len(info_items) > 1 else 'NA'
        Country = info_items[2].text.strip() if len(info_items) > 2 else 'NA'

    except Exception:
        Company = job_type = Country = 'NA'

    
    try:
        script_tag = soup.findAll("script", type="application/ld+json")[1]
        if script_tag:
            json_text = re.search(r'(?<=<script type="application/ld\+json">)(.*?)(?=</script>)', str(script_tag), re.DOTALL)
            if json_text:
                json_data = json_text.group(0).strip()
                try:
                    job_data = json.loads(json_data)
                    datePosted = job_data.get('datePosted', 'NA')
                    datePosted = datePosted.split('T')[0] if datePosted != 'NA' else 'NA'
                except:
                    datePosted = 'NA'
    except Exception:
        datePosted = 'NA'
                
    jobposting = {  
        "SRC_Title": title,  
        "SRC_Description": description,  
        "SRC_Country": Country,  
        "job_type": job_type,  
        "SRC_Company": Company,  
        "Link": job_link, 
        "date": datePosted,   
        "Website": "DiversityJobBoard"  
    }  

    return jobposting  

def save_to_excel(job_data):  
    if job_data:  
        df = pd.DataFrame(job_data)  
        df.to_excel("DiversityJobBoard.xlsx", index=False)  

def main():  
    job_links = get_job_links()  
    if not job_links:  
        return  

    driver = webdriver.Chrome()  
    job_data = []  
    for link_page in job_links:  
        job_posting = construct_job(driver, link_page)  
        if job_posting:  
            job_data.append(job_posting)  

    driver.quit() 
    save_to_excel(job_data)  

if __name__ == "__main__":  
    main() 



