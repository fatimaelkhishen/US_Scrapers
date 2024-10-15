from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC   
from selenium.common.exceptions import NoSuchElementException, TimeoutException  
from selenium import webdriver  
import time  
import pandas as pd  
import re  
from datetime import datetime, timedelta  

def get_job_links():  
    job_links = []  
    driver = webdriver.Chrome()  
    driver.get("https://www.lhh.com/us/en/search-jobs/?s=date&pg=1&t=&loc=United+States&rid=E8B32C77-F7A9-4344-8EC4-2C7CF5315ED6&range=25")  
    time.sleep(5)  
    base_url = "https://www.lhh.com"  
    p = 1    
    searching = True  
    try:    
        while searching: 
            url = f"{base_url}/us/en/search-jobs/?s=date&pg={p}&t=&loc=United+States&rid=E8B32C77-F7A9-4344-8EC4-2C7CF5315ED6&range=25"  
            driver.get(url)    
            time.sleep(5)  
            try:  
                cookie_consent_button = driver.find_element(By.XPATH, "//button[@id='onetrust-accept-btn-handler']")  
                cookie_consent_button.click()  
            except NoSuchElementException:  
                print("Cookie consent button not found, continuing...")  

            try:       
                WebDriverWait(driver, 30).until(  
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".c-job-listing-card"))  
                )  
            except TimeoutException:  
                print("Timeout waiting for elements to load.")  
                break  
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all("li", class_="c-job-listing-card")  

            if not listings:  
                print("No listings found on page", p)  
                break  

            for listing in listings:  
                job_link_tag = listing.find('a')   
                if job_link_tag and 'href' in job_link_tag.attrs:  
                    job_link = base_url + job_link_tag['href']  
                    job_links.append(job_link)  
   
            p += 1  

    finally:  
        driver.quit()  

    return job_links  
def transform_date(date_string):  
    if "day" in date_string:  
        days_ago = int(re.search(r'(\d+)', date_string).group(1))  
        return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')  
    elif "month" in date_string:  
        return (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')   
    elif "year" in date_string:  
        return (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')    
    else:  
         
        try:  
            parsed_date = datetime.strptime(date_string, '%B %d, %Y')  
            return parsed_date.strftime('%Y-%m-%d')  
        except ValueError:  
            return "NA"  

def construct_job(driver, job_link):  
    driver.get(job_link)  
    time.sleep(5)  
    soup = BeautifulSoup(driver.page_source, 'html.parser')   

      
    try:  
        jobTitle = soup.find("div", class_="c-job-details-mobile__header").find("p").text.strip()   
    except Exception:  
        jobTitle = "NA"        

    try:  
        Salary = soup.find_all("div", class_="c-job-details-mobile__information")[0].find("p", class_="c-job-details__category").text.strip()  
    except Exception:  
        Salary = "NA"   

    try:  
        Job_type = soup.find_all("div", class_="c-job-details-mobile__information")[1].find("p", class_="c-job-details__category").text.strip()  
    except Exception:  
        Job_type = "NA"  

    try:  
        Location = soup.find_all("div", class_="c-job-details-mobile__information")[2].find("p", class_="c-job-details__category").text.strip()  
    except Exception:  
        Location = "NA"   

    try:   
        companyName = soup.find("div", class_="employer-date-container").find_all("p")[0].text.strip()    
    except Exception:  
        companyName = "NA"  

    try:  
        Date_posted = soup.find("div", class_="employer-date-container").find_all("p")[1].text.strip()    
        Date_posted = transform_date(Date_posted)  
    except Exception:  
        Date_posted = "NA"  

    jobPosting = {  
        "SRC_Title": jobTitle,  
        "SRC_Company": companyName,    
        "SRC_Country": Location,    
        "Date_posted": Date_posted,  
        "SRC_Salary": Salary,  
        "SRC_Type": Job_type,  
        "Link": job_link,  
        "Website": "LHH"  
    }  

    return jobPosting
def save_to_excel(job_data):  
    df = pd.DataFrame(job_data)  
    df.to_excel("LHH.xlsx", index=False)  

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