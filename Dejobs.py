from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By  
from selenium import webdriver  
from selenium.common.exceptions import NoSuchElementException  
import time  
import pandas as pd  

def getJobs():  
    all_jobs = []  
    driver = webdriver.Chrome()  

    # Job posting URLs  
    url_bases = ["https://leidoscareers.dejobs.org", "https://marriottemployment.dejobs.org"]  

    for url_base in url_bases:  
        driver.get(url_base + "/usa/jobs/")  
       
        # Handle cookie consent  
        try:  
            cookie_consent_button = driver.find_element(By.CLASS_NAME, 'cookie-consent__button_accept')  
            cookie_consent_button.click()  
            time.sleep(1)  # Wait a moment after clicking  
        except NoSuchElementException:  
            print("No cookie consent button found.")  

        while True:  # Loop until no more jobs can be loaded  
            try:  
                more_jobs_button = driver.find_element(By.ID, 'button_moreJobs')  
                
                # If button is not displayed, break the loop  
                if more_jobs_button.get_attribute('style') == 'display: none;':  
                    print(f"No more jobs button visible for {url_base}.")  
                    break  

                # Scroll and click to load more jobs  
                driver.execute_script("arguments[0].scrollIntoView(true);", more_jobs_button)  
                more_jobs_button.click()  
                time.sleep(3)  # Allow time for new jobs to load  
                
            except NoSuchElementException:  
                print(f"Reached the last page on {url_base}. Moving to the next website.")  
                break  
            except Exception as e:  
                print(f"Unexpected error occurred: {str(e)}. Skipping to next website.")  
                break  

        # Parse the job postings from the loaded page  
        soup = BeautifulSoup(driver.page_source, 'html.parser')  
        job_postings = soup.findAll(class_="direct_joblisting")  

        for job in job_postings:  
            link = url_base + job.find('a')['href']  
            all_jobs.append({'link': link, 'SRC_Country': 'USA'})  

    driver.quit()  
    return all_jobs  

def construct_job(driver, job_link):  
    driver.get(job_link)  
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')  

    # Safely retrieve job data  
    try:  
        title = soup.find(itemprop='title').text  
    except Exception:  
        title = "NA"  
    try:  
        description = soup.find(id='direct_jobDescriptionText').text.replace('\n', '').strip()  
    except Exception:  
        description = "NA"  
    try:  
        datePosted = soup.find(itemprop='datePosted')['content'].split('T')[0]  
    except Exception:  
        datePosted = "NA"  
    try:  
        companyName = soup.find(itemprop='hiringOrganization').text.strip()  
    except Exception:  
        companyName = "NA"  
    location = "USA"  # Assuming location is always USA  
    
    jobPosting = {  
        'SRC_Title': title,  
        'SRC_Company': companyName,  
        'SRC_Country': location,  
        'Posting_Date': datePosted,  
        'SRC_Description': description,  
        'Link': job_link  
    }  
    return jobPosting  

def save_to_excel(job_data):  
    df = pd.DataFrame(job_data)  
    df.to_excel("jobs.xlsx", index=False, engine='openpyxl')  

def main():  
    job_links = getJobs()  
    driver = webdriver.Chrome()  
    job_data = []  
    for link in job_links:  
        job_posting = construct_job(driver, link['link'])  
        job_data.append(job_posting)  
    driver.quit()  
    save_to_excel(job_data)  

if __name__ == "__main__":  
    main()