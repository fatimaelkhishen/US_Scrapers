import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

def get_job_links():
    job_links = []
    driver = webdriver.Chrome()
    driver.get("https://www.themuse.com/search/location/united-states/radius/100mi/")

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "JobCard_jobCardClickable__ZR6Sk"))
        )

       
        extract_job_links(driver, job_links)

        while True: 
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load More Results')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
                load_more_button.click()
                time.sleep(random.uniform(2, 5))  

                
                extract_job_links(driver, job_links)

            except Exception as e:
                break  

    finally:
        driver.quit()  

    return job_links

def extract_job_links(driver, job_links):
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    listings = soup.find_all("div", class_="JobCard_jobCardClickable__ZR6Sk")

    
    for listing in listings:
        job_link_tag = listing.find("a", class_="JobCard_viewJobLink__Gesny")
        if job_link_tag and 'href' in job_link_tag.attrs:
            full_link = job_link_tag['href']
            if not full_link.startswith('http'):
                full_link = "https://www.themuse.com" + full_link
            if full_link not in job_links:  
                job_links.append(full_link)

def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    
    try:
        title = soup.find('h1', class_="JobIndividualHeader_jobHeaderTitle__wA3d3").text.strip()
    except Exception as e:
        title = "NA"
        

    try:
        # Find the script tag containing JSON data
        script_tag = soup.find("script", type="application/ld+json")
        if script_tag:
            json_text = script_tag.string.strip()
            try:
                job_data = json.loads(json_text)
                datePosted = job_data.get('datePosted', 'NA')
                datePosted = datePosted.split('T')[0] if datePosted != 'NA' else 'NA'
            except json.JSONDecodeError as e:
                datePosted = 'NA'
               
        else:
            datePosted = 'NA'
    except Exception as e:
        datePosted = 'NA'
        

    try:
        desc = soup.find('article', class_="JobIndividualBody_jobBodyDescription__NTB3f").text.strip()
    except Exception as e:
        desc = "NA"
       

    try:
        company_name_tag = soup.find('a', class_="JobIndividualHeader_jobHeaderCompanyName__PKqdn")
        company_name = company_name_tag.text.strip() if company_name_tag else "NA"
    except Exception as e:
        company_name = "NA"
      

    try:
        location = soup.find('span', class_="JobIndividualHeader_jobHeaderLocation__Tyroc").text.strip()
    except Exception as e:
        location = "NA"
        

   
    jobposting = {
        "SRC_Title": title,
        "SRC_Description": desc,
        "SRC_location": location,
        "SRC_Company": company_name,
        "Link": job_link,
        "date": datePosted,
        "Website": "Themuse"
    }

    return jobposting

def save_to_excel(job_data):
    if job_data:
        df = pd.DataFrame(job_data)
        df.to_excel("Themuse.xlsx", index=False)  
        print("Job postings have been saved to 'Themuse.xlsx'.")

def main():
    job_links = get_job_links()
    if not job_links:
        print("No job links found.")
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
