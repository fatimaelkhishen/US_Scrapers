import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def get_job_links():
    job_links = []
    driver = webdriver.Chrome()
    driver.get("https://eaglejobs.org/job-openings/?job__location_spec=%25d8%25a3%25d9%2585%25d8%25b1%25d9%258a%25d9%2583%25d8%25a7")
    try:
        while True:
            # Count number of jobs
            curr_jobs_num = len(driver.find_elements(By.CLASS_NAME, "awsm-job-listing-item awsm-job-expired-item awsm-grid-item"))
            try:
                # try to wait for the load more button to be clickable
                WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#content > article > div > div > div.awsm-job-listings.awsm-row.awsm-grid-col-2 > div.awsm-jobs-pagination.awsm-load-more-main > a")))
            except :
                print('Finished scrolling')
                break
            # click button using javascript
            driver.execute_script('document.querySelector("#content > article > div > div > div.awsm-job-listings.awsm-row.awsm-grid-col-2 > div.awsm-jobs-pagination.awsm-load-more-main > a").click()') 
            # wait for the new jobs to be loaded
            WebDriverWait(driver, 10).until(lambda driver: curr_jobs_num != len(driver.find_elements(By.CLASS_NAME, "awsm-job-listing-item")))  # Add a sleep to allow new job listings to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        jobListings = soup.find_all("div",class_='awsm-job-listing-item awsm-job-expired-item awsm-grid-item')
        for job in jobListings:
                job_links.append(job.find('a')['href'])
    except Exception as e:
        print("error")

    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        title = soup.find("h2",class_='single-post-title entry-title').text
    except:
        title = "NA"
    try:
        category = soup.find(
            'div', class_='awsm-job-specification-item awsm-job-specification-job-category').text.replace('تصنيف الوظيفة: ', '')
    except:
        category = "NA"
    try:
        jobType = soup.find(
            'div', class_='awsm-job-specification-item awsm-job-specification-job-type').text.replace('نوع الوظيفة: ', '')
    except:
        jobType = "NA"
    try:
        location = soup.find(
            'div', class_='awsm-job-specification-item awsm-job-specification-job-location').text.replace('مقر العمل: ', '')
    except:
        location = "NA"
    try:
        company = soup.find('div',class_='awsm-job-specification-item awsm-job-specification-company').text.replace('اسم الشركة:','')
    except:
        company = "NA"
    try:
        salary = soup.find('div',class_='awsm-job-specification-item awsm-job-specification-rateb').text.replace('الراتب:','')
    except:
        salary = "NA"
        
    try:
        description = soup.find('div', id='formToggleSheet').text
    except:
        description = "NA"
    try:
        script = soup.find('script', {'type': 'application/ld+json'})
        data_dict = json.loads(script.string)
        datestr = data_dict["@graph"][0]["datePublished"]
        PostingDate = re.search('\d{4}-\d{2}-\d{2}', datestr).group(0)
    except:
        PostingDate = "NA"
    jobPosting = {
        'SRC_Title': title,
        'SRC_Company':company,
        'SRC_Description': description,
        'Link': job_link,
        'SRC_Category': category,
        'Job_Type': jobType,
        'SRC_Salary':salary,
        'SRC_Country': location,
        'Posting_Date': PostingDate,
        'Website': 'Eaglejobs'
    }
    return jobPosting

def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Eagle.xlsx", index=False)

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