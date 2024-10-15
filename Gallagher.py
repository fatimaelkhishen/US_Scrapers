from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC   
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException  
from selenium import webdriver  
import time  
import pandas as pd  

def get_job_links(driver):  
    job_links = []   
    base_url = "https://jobs.ajg.com"  
    p = 1  
    searching = True  

    while searching:  
        try:  
            url = f"{base_url}/ajg-home/jobs?location=united%20states&stretch=10&stretchUnit=MILES&page={p}"  
            driver.get(url)  
            WebDriverWait(driver, 10).until(  
                EC.presence_of_element_located((By.CSS_SELECTOR, ".mat-expansion-panel"))  
            )  

            # Accept cookies if the button is present  
            try:  
                cookie_consent_button = driver.find_element(By.XPATH, '//*[@id="CookieReportsBanner"]/div[1]/div[2]/a[1]')  
                cookie_consent_button.click()  
            except NoSuchElementException:  
                pass  

            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all(class_="mat-expansion-panel")  
     
            if not listings:  # Break if no job listings found  
                break  

            for listing in listings:  
                job_link_tag = listing.find('a')   
                if job_link_tag and 'href' in job_link_tag.attrs:  
                    job_link = base_url + job_link_tag['href']  
                    job_links.append(job_link)  
             
            p += 1  

        except WebDriverException:
            break

    return job_links  

def construct_job(driver, job_link):   
    try:
        driver.get(job_link)  
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'article#description-body'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')  

        jobPosting = {  
            'SRC_Title': "NA",  
            'SRC_Country': "NA",  
            'SRC_Category': "NA",  
            'SRC_Type': "NA",  
            'Website': 'Gallagher',  
            'SRC_Description': "NA"  
        }  

        try:  
            title = soup.find('h1', {'itemprop': 'title'}).text.strip()   
            jobPosting['SRC_Title'] = title  
        except Exception:
            pass
        
        try:  
            location = soup.find('li', id="header-locations").text.strip()  
            jobPosting['SRC_Country'] = location  
        except Exception:
            pass
        
        try:  
            job_category = soup.find('li', id='header-categories').text.strip()  
            jobPosting['SRC_Category'] = job_category  
        except Exception:
            pass
        
        try:  
            job_type = soup.find('li', id='header-tags3').text.strip()  
            jobPosting['SRC_Type'] = job_type  
        except Exception:
            pass
        
        try:  
            desc = soup.find('article', id='description-body').text.strip()   
            jobPosting['SRC_Description'] = desc  
        except Exception:
            pass

        return jobPosting
    
    except WebDriverException:
        return None

def save_to_excel(job_data):  
    if job_data:
        df = pd.DataFrame(job_data)  
        df.to_excel("Gallagher.xlsx", index=False)  
        print("Data successfully exported to Gallagher.xlsx")

def main():  
    driver = webdriver.Chrome()  
    try:
        job_links = get_job_links(driver)  
        if not job_links:  
            return  

        job_data = []  
        for link in job_links:  
            job_posting = construct_job(driver, link)  
            if job_posting:  
                job_data.append(job_posting)  

        save_to_excel(job_data)  
    
    finally:
        driver.quit()  

if __name__ == "__main__":  
    main()