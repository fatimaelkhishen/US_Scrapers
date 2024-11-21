import json  
import datetime  
import pandas as pd  
from openpyxl import Workbook  
import os  

def run_scraper(scraper_name):  
    try:  
        module = __import__(scraper_name.lower())  
        return module.run_scraper()  # Assume each module has a function named run_scraper  
    except Exception as e:  
        raise RuntimeError(f"Error running {scraper_name}: {str(e)}")  

def test_scrapers(config_file):  
    # Load scraper configurations  
    with open(config_file, 'r') as f:  
        config = json.load(f)  
    
    results = []  

    for scraper in config['scrapers']:  
        scraper_name = scraper['name']  
        module_name = scraper['module']  
        try:  
            data = run_scraper(module_name)  
            if isinstance(data, dict) and len(data) > 0:  
                results.append({"name": scraper_name, "status": "Success", "error": ""})  
            else:  
                results.append({"name": scraper_name, "status": "Failed", "error": "Returned data is not valid"})  
        except Exception as e:  
            results.append({"name": scraper_name, "status": "Failed", "error": str(e)})  

    return results  

def save_results_to_excel(results):  
    today = datetime.datetime.now().strftime("%Y-%m-%d")  
    filename = f"scraper_test_results_{today}.xlsx"  

    # Convert results to DataFrame  
    df = pd.DataFrame(results)  

    # Save to Excel  
    df.to_excel(filename, index=False)  
    print(f"Results saved to {filename}")  

if __name__ == "__main__":  
    print("Current working directory:", os.getcwd())  # Print current working directory  
    config_file = 'config.json'  # Adjust this path if necessary  
    results = test_scrapers(config_file)  
    save_results_to_excel(results)