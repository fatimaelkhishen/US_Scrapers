import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


def get_job_links():
    job_links = []
    driver = webdriver.Chrome()
    page = 1
    searching = True
    while searching:
        url = f"https://indevjobs.org/?country=187&page={page}"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source , 'html.parser')
        
        
        pagination_box = soup.find('div', class_='pagination-box')
        if pagination_box:
            
            page_info = pagination_box.find('h5').get_text()
            if 'Page' in page_info:
                page_numbers = [int(s) for s in page_info.split() if s.isdigit()]
                current_page, total_pages = page_numbers
                if current_page == total_pages:  
                    searching = False
        
        jobboxes = soup.find_all('div', class_='col-md-4')
        if jobboxes:
            for item in jobboxes:
                href = item.find('a')['href']
                if href == '#':
                    pass
                else:
                    job_links.append(href)
        page += 1
    driver.quit()
    return job_links

def construct_job(driver, job_link):  
    driver.get(job_link)  
    soup = BeautifulSoup(driver.page_source, 'html.parser')  

    
    try:  
        jobTitle = soup.find("h4", class_="inner-job").text.strip()  
    except Exception:  
        jobTitle = "NA"  

    try:  
        companyName = soup.find("div", class_="job-short-desc").find("p").text.strip()  
    except Exception:
        companyName = "NA"   

    try:  
        years_of_experience = soup.find("div", class_="job-short-desc").findAll("p")[2].text.strip()  
    except Exception:  
        years_of_experience = "NA"  

    try:  
        required_skill = soup.find("div", class_="job-short-desc").findAll("p")[3].text.strip()  
    except Exception:  
        required_skill = "NA"   

    try:  
        jobDescription = soup.find("div", class_="ijobs_listing_left_sidebar_wrapper").text.replace("\xa0", " ").replace('\n', " ").strip()  
    except Exception:  
        jobDescription = "NA"

    try:  
        location = soup.find("div", class_="job-short-desc").findAll("p")[1].text.strip()  
    except Exception:  
        location = "NA"

    try:  
        deadline = soup.find("div", class_="job-footer").text.split(":")[1].strip()  
    except Exception:  
        deadline = "NA"  

    jobPosting = {  
        "SRC_Title": jobTitle,  
        "SRC_Company": companyName,  
        "Required Skill": required_skill,  
        "Apply By": deadline,  
        "SRC_Description": jobDescription,  
        "SRC_Country": location,  
        "Years of experience": years_of_experience,   
        "Link": job_link,  
        "Website": "Indevjobs"  
    }  

    return jobPosting
def save_to_excel(job_data):
    df = pd.DataFrame(job_data)
    df.to_excel("Indevjobs.xlsx", index=False)

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