from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium import webdriver
import time
import pandas as pd


def getJobs():
        all_jobs = []
        driver = webdriver.Chrome()

        url_base = "https://jobsus.deloitte.com"
        driver.get(url_base + "/usa/jobs/")

        try:
            cookie_consent_button = driver.find_element(By.CLASS_NAME, 'cookie-consent__button_accept')
            cookie_consent_button.click()
        except NoSuchElementException:
            pass
            

        while True:
            try:
                more_jobs_button = driver.find_element(By.ID, 'button_moreJobs')
                if more_jobs_button.get_attribute('style') == 'display: none;':
                    print(f"No more jobs button visible for {url_base}. Moving to the next website.")
                    break  

                driver.execute_script("arguments[0].scrollIntoView(true);", more_jobs_button)
                driver.execute_script("arguments[0].click();", more_jobs_button)
                time.sleep(3)  
            except NoSuchElementException:
                print(f"Reached the last page on {url_base}. Moving to the next website.")
                break
            except Exception as e:
                print(f"Unexpected error occurred: {str(e)}. Skipping. Moving to the next website.")
                break  

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

    try:
        title = soup.find(itemprop='title').text
    except:
        title = "NA"
    try:
        description = soup.find(id='direct_jobDescriptionText').text.replace('\n', '').strip()
    except:
        description = "NA"
    try:
        datePosted = soup.find(itemprop='datePosted')['content'].split('T')[0]
    except:
        datePosted = "NA"
    try:
        companyName = soup.find(class_='direct_jobListingCompany').text.strip()
    except:
        companyName = "NA"
    try:
        location = "USA"
    except:
        location = "NA"
    jobPosting = {
        'SRC_Title': title,
        'SRC_Company': companyName,
        'SRC_Country': location,
        'Posting_Date': datePosted,
        'SRC_Description': description,
        'Link': job_link
    }
    return jobPosting
# job_links = getJobs()
# driver = webdriver.Chrome()
# print(job_links)

def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("jobs.xlsx", index=False)


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
