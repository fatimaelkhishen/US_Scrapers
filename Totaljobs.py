import pandas as pd  
from bs4 import BeautifulSoup  
from selenium import webdriver  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import re
import time  
import random  

def get_job_links(driver):  
    job_links = []  
    p = 1  

    try:  
        while True:  
            url = f"https://www.totaljobs.com/jobs/in-united-states?radius=10&searchOrigin=Homepage_top-search&page={p}"  
            driver.get(url)  
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "res-1p8f8en")))  
            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            job_cards = soup.find_all("article", class_="res-1p8f8en")  
            print(f"Page {p} - Found {len(job_cards)} job cards.")  # Debugging output  

            if not job_cards:  
                break  

            for job_card in job_cards:  
                title = job_card.find("h2", class_="res-1tassqi")  
                if title:  
                    link = title.find('a').get('href')  
                    if not link.startswith("https://www."):
                        job_links.append("https://www.totaljobs.com" + link)
  

            # Navigate to the next page  
            next_button = soup.find("button", {"aria-label": "Next"})  
            if next_button and "disabled" in next_button.attrs:  
                print("No more pages to navigate.")  # Debugging output  
                break  

            p += 1   
            time.sleep(random.uniform(2, 5))  # Randomized sleep time  
    except Exception as e:  
        print(f"An error occurred while getting job links: {e}")  
    return job_links

def construct_job(driver, job_link):  
    try:  
        driver.get(job_link)  
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'job-ad-display-gro348')))  
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
           title = soup.find('h1', class_='job-ad-display-29uigd').text.strip()
        except:
           title = "NA"
        try: 
           company = soup.find('li', class_='at-listing__list-icons_company-name job-ad-display-62o8fr').text.strip()
        except:
           company = "NA"
        try:             
           location = soup.find('li', class_='at-listing__list-icons_location map-trigger job-ad-display-62o8fr').text.strip()
        except:
           location = "NA"
        try:
            dateposted = soup.find('li', class_='at-listing__list-icons_date job-ad-display-62o8fr').text.replace("Published:", "").strip()
    
    # Initialize delta as zero
            delta = timedelta()

            # Match for weeks and days
            match = re.search(r'(\d+)\s*(weeks?|days?)\s*ago', dateposted)
            if match:
               number = int(match.group(1))
               unit = match.group(2)
               
               # Calculate the timedelta based on the unit
               if 'week' in unit:
                     delta += timedelta(weeks=number)
               else:
                     delta += timedelta(days=number)

            # Match for hours and minutes
            match_hour = re.search(r'(\d+)\s*(hours?|minutes?)\s*ago', dateposted)
            if match_hour:
               number = int(match_hour.group(1))
               unit = match_hour.group(2)

               # Calculate the timedelta based on the unit
               if 'hour' in unit:
                     delta += timedelta(hours=number)
               else:
                     delta += timedelta(minutes=number)

            # Get the current date and subtract the delta
            published_date = datetime.now() - delta
            
            # Format the date to YMD
            dateposted = published_date.strftime('%Y-%m-%d')
          
        except:
           dateposted = "NA"
        try:   
           salary = soup.find("li", class_="at-listing__list-icons_salary job-ad-display-1dus89x").text.strip()
        except:
           salary = "NA"  
        try:
           job_type = soup.find("li", class_="at-listing__list-icons_work-type job-ad-display-62o8fr").text.strip() 
        except:
           job_type = "NA"
        try:
           desc = soup.find('div', class_='at-section-text-jobDescription-content listingContentBrandingColor job-ad-display-1b1is8w').text.strip() 
        except:
           desc = "NA"

        return {  
            'SRC_Title': title,  
            'SRC_Company': company,  
            'SRC_Country': location,  
            'Posting_date': dateposted,  
            'SRC_Salary': salary,  
            'SRC_Type': job_type,  
            'Job_Link': job_link,  
            'SRC_Description': desc,  
            'Website': 'Totaljobs'  
        }  
    except Exception as e:  
        print(f"Error while fetching job details from {job_link}: {e}")  
        return None  

def save_to_excel(job_data):  
    df = pd.DataFrame(job_data)  
    df.to_excel("Totaljobs.xlsx", index=False)  

def main():  
    driver = webdriver.Chrome()  
    job_links = get_job_links(driver)  
    job_data = []  
    failed_links = []  

    for link in job_links:  
        job_posting = construct_job(driver, link)  
        if job_posting:  
            job_data.append(job_posting)  
        else:  
            failed_links.append(link)  

    driver.quit()  
    save_to_excel(job_data)  

    if failed_links:  
        print(f"Failed to fetch details for the following links: {failed_links}")  

if __name__ == "__main__":  
    main()