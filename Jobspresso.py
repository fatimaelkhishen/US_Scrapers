from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By  
from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException, TimeoutException  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
import time  
import pandas as pd  
import json  

def getJobs():  
    all_jobs = []  
    unique_links = set()  # Set to store unique job links  
    driver = webdriver.Chrome()  
    url_base = "https://jobspresso.co/"  
    driver.get(url_base)  

    # Initialize current_page to 1  
    current_page = 1  

    while True:  
        try:  
            # Wait for the "Load More" button to be visible  
            more_jobs_button = WebDriverWait(driver, 10).until(  
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'a.load_more_jobs'))  
            )  

            driver.execute_script("arguments[0].scrollIntoView(true);", more_jobs_button)  
            driver.execute_script("arguments[0].click();", more_jobs_button)  
            time.sleep(3)  # Wait for jobs to load  

            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            job_postings = soup.findAll("li", class_="job_listing")  

            

            if len(job_postings) == 0:  
                print("No more job postings found on this page. Exiting.")  
                break  

            for job in job_postings:  
                link = job.find('a')['href']    

                # Check if the link is already in the set of unique links  
                if link not in unique_links:  
                    all_jobs.append({'link': link})  
                    unique_links.add(link)  # Add the link to the set to track it as seen  

            current_page += 1  

        except (NoSuchElementException, TimeoutException):  
            print("No more job postings can be loaded or the 'Load More' button is not available. Exiting.")  
            break   

    driver.quit()  
    return all_jobs  

def construct_job(driver, job_link):  
    driver.get(job_link)  
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')  

    try:  
        title = soup.find("h1", class_='page-title').text  
    except Exception:  
        title = "NA"  
    try:  
        companyName = soup.find("li", class_='job-company').text.strip()  
    except Exception:  
        companyName = "NA"  
    try:  
        description = soup.find("div", class_="job_listing-description job-overview col-md-10 col-sm-12").text.strip()  
    except Exception:  
        description = "NA"  
    try:  
        location = soup.find(itemprop='jobLocation').text.strip()  
    except Exception:  
        location = "NA"  
    try:  
        jobtype = soup.find(itemprop='employmentType').text.strip()  
    except Exception:  
        jobtype = "NA"   

     
    if 'US' not in location and 'USA' not in location and 'United States' not in location:  
        return None   

    try:  
        script_tag = soup.find("script", type="application/ld+json")  
        if script_tag:  
            json_text = script_tag.string.strip()  
            try:  
                job_data = json.loads(json_text)  
                datePosted = job_data.get('datePosted', 'NA')  
                datePosted = datePosted.split('T')[0] if datePosted != 'NA' else 'NA'  
            except json.JSONDecodeError:  
                datePosted = 'NA'  
        else:  
            datePosted = 'NA'    
    except Exception:  
        datePosted = 'NA'  

    jobPosting = {  
        'SRC_Title': title,  
        'SRC_Company': companyName,  
        'SRC_Country': location,  
        'Posting_Date': datePosted,  
        'SRC_Description': description,  
        'SRC_Type': jobtype,  
        'Link': job_link  
    }  
    return jobPosting  

def save_to_excel(job_data):  
    if job_data:    
        df = pd.DataFrame(job_data)  
        df.to_excel("jobspresso.xlsx", index=False, engine='openpyxl')  
        print("Job data has been saved to jobspresso.xlsx.")  
    else:  
        print("No job data to save.")  

def main():  
    job_links = getJobs()  
    if not job_links:  
        print("No job links were found.")  
        return  

    driver = webdriver.Chrome()  
    job_data = []  
    for link in job_links:  
        job_posting = construct_job(driver, link['link'])  
        if job_posting:  
            job_data.append(job_posting)  

    driver.quit()  
    save_to_excel(job_data)  

if __name__ == "__main__":  
    main()