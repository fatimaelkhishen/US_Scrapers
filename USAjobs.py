import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_job_links():
    job_links = []
    driver = webdriver.Chrome()
    base_url = "https://www.usajobs.gov/Search/Results?l=United%20States&d=ST&hp=public&p="
    page_number = 1

    try:
        while True:
            # Navigate to the page based on the current page number
            driver.get(base_url + str(page_number))
            time.sleep(5)  # Allow the page to load

            try:
                WebDriverWait(driver, 45).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".usajobs-search-result--core"))
                )
            except TimeoutException:
                print(f"Timed out waiting for page {page_number} to load.")
                break  # Exit the loop if the page does not load properly

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            listings = soup.find_all("div", class_="usajobs-search-result--core")

            if not listings:
                print(f"No listings found on page {page_number}, ending search.")
                break  # If no listings are found, break the loop (end of pages)

            for listing in listings:
                try:
                    job_link = listing.find("a")['href']
                    if job_link:
                        if job_link.startswith('/'):
                            job_link = "https://www.usajobs.gov" + job_link
                        job_links.append((job_link, page_number))
                except Exception as e:
                    print(f"Error parsing job link: {e}")

            # Check if there are no more pages to paginate
            try:
                next_button = soup.find("a", class_="usajobs-search-pagination__next-page")
                if not next_button or "disabled" in next_button.get('class', []):
                    print("No 'Next' button found or it's disabled, ending pagination.")
                    break  # Break if there is no "Next" button or it's disabled
            except Exception as e:
                print(f"Error finding 'Next' button: {e}")
                break

            page_number += 1  # Increment the page number to get the next page

    finally:
        driver.quit()

    return job_links

def construct_job(driver, job_link_page):
    job_link, _ = job_link_page

    if not job_link or not job_link.startswith(('http://', 'https://')):
        return None

    driver.get(job_link)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "usajobs-joa-banner__title"))
    )
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        title = soup.find("h1", class_="usajobs-joa-banner__title").text.strip()
    except Exception:
        title = 'NA'

    try:
        description = soup.find(id='summary').text.replace('\n', '').strip()
    except Exception:
        description = 'NA'

    try: 
        company = soup.find('div', class_='usajobs-joa-banner__dept').text.strip()
    except:
        company = "NA"

    
    try:             
        location = soup.find('div', class_='usajobs-joa-locations__body').text.strip()
    except:
        location = "NA"
        
    try:   
        salary = soup.find("p", class_="usajobs-joa-summary__salary salary-text-normal").text.strip()
    except:
        salary = "NA"

    # Extract open & closing dates
    try:
        open_close_dates = soup.find("li", class_="usajobs-joa-summary__item usajobs-joa-summary--beta__item")
        date_span = open_close_dates.find_all("span", itemprop=True)
        date_posted = date_span[0].text.strip()
        valid_through = date_span[1].text.strip()
    except Exception:
        date_posted = 'NA'
        valid_through = 'NA'

    jobposting = {
        "SRC_Title": title,
        "SRC_Description": description,
        "SRC_Country": location,
        'SRC_Salary': salary, 
        "SRC_Company": company, 
        "SRC_Date_Posted": date_posted,
        "SRC_Valid_Through": valid_through,
        "Link": job_link,
        "Website": "USAjobs"
    }

    return jobposting

def save_to_excel(job_data):
    if job_data:
        df = pd.DataFrame(job_data)
        df.to_excel("USAjobs.xlsx", index=False)

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