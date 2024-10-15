from bs4 import BeautifulSoup  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC   
from selenium.common.exceptions import TimeoutException  
from selenium import webdriver  
import pandas as pd  
import time  

def get_job_links():  
    job_links = []   
    driver = webdriver.Chrome()  
    base_url = "https://www.flexjobs.com"  
    p = 1  

    try:  
       
        while True:  

            url = f"{base_url}/search?joblocations=united%20states&usecLocation=true&Loc.LatLng=0%2C0&Loc.Radius=30&page={p}"  
            driver.get(url)  
            print(f"Accessing: {url}")  
            time.sleep(5)  

            try:  
                WebDriverWait(driver, 30).until(  
                    EC.presence_of_element_located((By.CLASS_NAME, "sc-14nyru2-2"))  
                )  
            except TimeoutException:  
                print("Timeout while waiting for elements to load. Exiting...")  
                break  

            soup = BeautifulSoup(driver.page_source, 'html.parser')  
            listings = soup.find_all("div", class_="sc-14nyru2-2")  

            if not listings:   
                print("No more listings found.")  
                break  

            for listing in listings:  
                job_link_tag = listing.find('a', id=lambda x: x and x.startswith('job-name-'))  
                if job_link_tag and 'href' in job_link_tag.attrs:  
                    job_link = base_url + job_link_tag['href']  
                    job_links.append(job_link)  
             
            p += 1  

    finally:  
        driver.quit()  

    return job_links  

def construct_job(driver, job_link):  
    driver.get(job_link)  
    soup = BeautifulSoup(driver.page_source, 'html.parser')  

    jobPosting = {}  

    # Extracting Job Title  
    try:  
        title_tag = soup.find("h1")  
        job_title = title_tag.text.strip() if title_tag else "NA"  
    except Exception as e:  
        job_title = "NA"  
        print(f"Error extracting job title: {e}")  

    # Extracting Posting Date  
    try:  
        posting_date_tag = soup.find("p", class_="sc-3znpb9-12 hFMoxy")  
        posting_date = posting_date_tag.text.strip() if posting_date_tag else "NA"  
    except Exception as e:  
        posting_date = "NA"  
        print(f"Error extracting posting date: {e}")  

    # Extracting Salary  
    try:    
        salary = driver.find_element(
                By.XPATH, "/html/body/div[1]/div/main/div/div/div/div[2]/ul/li[2]/p")
    except Exception as e:  
        salary = "NA"  
        print(f"Error extracting salary: {e}")  

    # Extracting Remote Work Level  
    try:  
        remote_work_level_tag = soup.find("h5", string="Remote Work Level:")  
        remote_work_level = remote_work_level_tag.find_next("p").text.strip() if remote_work_level_tag else "NA"  
    except:  
        remote_work_level = "NA"  
    
    # Extracting Company  
    try:  
        company_tag = soup.find("h5", string="Company:")  
        company = company_tag.find_next("p").text.strip() if company_tag else "NA"  
    except:  
        company = "NA"  

    # Extracting Job Type  
    try:  
        job_type_tag = soup.find("h5", string="Job Type:")  
        job_type = job_type_tag.find_next("p").text.strip() if job_type_tag else "NA"  
    except:  
        job_type = "NA"  

    # Extracting Job Schedule  
    try:  
        job_schedule_tag = soup.find("h5", string="Job Schedule:")  
        job_schedule = job_schedule_tag.find_next("p").text.strip() if job_schedule_tag else "NA"  
    except:  
        job_schedule = "NA"  

    # Extracting Career Level  
    try:  
        career_level_tag = soup.find("h5", string="Career Level:")  
        career_level = career_level_tag.find_next("p").text.strip() if career_level_tag else "NA"  
    except:  
        career_level = "NA"  

    # Extracting Travel Required  
    try:  
        travel_required_tag = soup.find("h5", string="Travel Required:")  
        travel_required = travel_required_tag.find_next("p").text.strip() if travel_required_tag else "NA"  
    except:  
        travel_required = "NA"  

    # Extracting Categories  
    try:  
        categories_tag = soup.find("h5", string="Categories:")  
        categories = categories_tag.find_next("p").text.strip() if categories_tag else "NA"  
    except:  
        categories = "NA"  

    # Compiling all information into a dictionary  
    jobPosting = {  
        'Job_Title': job_title,  
        'Posting_Date': posting_date,  
        'Salary': salary,  
        'Remote_Work_Level': remote_work_level,  
        'Company': company,  
        'Job_Type': job_type,  
        'Job_Schedule': job_schedule,  
        'Career_Level': career_level,  
        'Travel_Required': travel_required,   
        'Categories': categories,  
        'Link': job_link  
    }  

    return jobPosting  

def save_to_excel(job_data):  
    df = pd.DataFrame(job_data)  
    df.to_excel("flexjobs.xlsx", index=False)  

def main():  
    job_links = get_job_links()  
    driver = webdriver.Chrome()  
    job_data = []  
    
    try:  
        for link in job_links:  
            job_posting = construct_job(driver, link)  
            job_data.append(job_posting)  
    finally:  
        driver.quit()  
        
    save_to_excel(job_data)  

if __name__ == "__main__":  
    main()