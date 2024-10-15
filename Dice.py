import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
import re

def get_job_links():
    job_links = []
    p = 0

    driver = webdriver.Chrome()
    while True:
        url = f"https://www.dice.com/jobs?location=United%20States&latitude=37.09024&longitude=-95.712891&countryCode=US&locationPrecision=Country&radius=30&radiusUnit=mi&page={p}"

        driver.get(url)
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "ng-star-inserted")))
        
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all("div", class_="card search-card")
        for job_card in job_cards:
            link = job_card.find('a').get('id')
            job_links.append("https://www.dice.com/job-detail/"+link)
        button = soup.find("li", class_="pagination-next page-item ng-star-inserted")
        if not button:
            break
        p+=1
    driver.quit()
    return job_links

def construct_job(driver, job_link):
    driver.get(job_link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        button = soup.findAll("li", class_="pagination-next page-item ng-star-inserted")
        button.click()
    except:
        pass
    try:
        title = soup.find('h1', class_='flex flex-wrap text-center ml-auto mr-auto md:text-left md:flex-col md:flex-nowrap lg:col-span-7 md:ml-0 font-[700]').text.strip()
    except:
        title = "NA"

    try:
        posted_date_element = soup.find('li', {'data-testid': 'legalInfo-originallyPosted'}).find('dhi-time-ago')

        posted_date = posted_date_element['posted-date'].split('T')[0]
    except:
        posted_date = "NA"

    try:
        company = soup.find('a', {'data-cy': 'companyNameLink'}).text.strip()
    except:
        company = "NA"

    try:
        Skills = soup.find('div', {'data-cy': 'skillsList'}).text.split()
    except:
        Skills = "NA"

    try:
        location = soup.find('li', {'data-cy': 'location'}).text.strip()
    except:
        location = "NA"
    try:
        desc = soup.find('div', class_='job-details_jobDetails___c7LA').text.strip()
    except:
        desc = "NA"

    jobPosting = {
        'SRC_Title': title,
        'SRC_Company': company,
        'SRC_Country': location,
        'Posting_date': posted_date,
        'Job_Link': job_link,
        'Website': 'Dice',
        'SRC_Skills': Skills,
        'SRC_Description': desc
    }
    return jobPosting

def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Dice.xlsx", index=False)

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
