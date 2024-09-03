from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json
import time

def fetch_job_details(driver, job_element):
    job_data = {}
    try:
        # Click on the job title to open detailed view
        title_element = job_element.find_element(By.CLASS_NAME, 's-18')
        title_element.click()

        # Wait for the detailed view to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'jcnt')))

        # Extract gender information
        try:
            gender_element = driver.find_element(By.XPATH, "//b[text()='Gender']/following-sibling::div")
            job_data['gender'] = gender_element.text.strip()
        except NoSuchElementException:
            job_data['gender'] = "Not specified"

        # Other job details
        job_data['title'] = title_element.get_attribute('title')
        job_data['company'] = job_element.find_element(By.CLASS_NAME, 'cname').text.strip()
        job_data['description'] = job_element.find_element(By.CLASS_NAME, 'jbody').text.strip()
        job_data['posted_on'] = job_element.find_element(By.CSS_SELECTOR, 'span[data-original-title="Posted On"]').text.strip()
        job_data['experience'] = job_element.find_element(By.CSS_SELECTOR, '.func-area-drn').text.strip()
        
        try:
            job_data['salary'] = job_element.find_element(By.CSS_SELECTOR, 'span[data-original-title="Offer Salary - PKR"] span').text.strip()
        except NoSuchElementException:
            job_data['salary'] = "Not specified"

        # Navigate back to the job list
        driver.back()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'job')))

    except Exception as e:
        print(f"Error processing job details: {e}")

    return job_data

def fetch_jobs_from_page(driver, job_number):
    url = f'https://www.rozee.pk/job/jsearch/q/all/fin/1/fpn/{job_number}'
    driver.get(url)

    wait = WebDriverWait(driver, 80)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'job')))

    job_elements = driver.find_elements(By.CLASS_NAME, 'job')
    
    print(f"Found {len(job_elements)} job elements on page {job_number//20 + 1}.")

    jobs_data = []

    for job in job_elements:
        job_data = fetch_job_details(driver, job)
        if job_data:
            jobs_data.append(job_data)
        time.sleep(1)  # Add a small delay between job scrapes

    return jobs_data

def fetch_all_jobs():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    all_jobs_data = []
    
    for job_number in range(0, 481, 20):  # Goes up to 460
        page_jobs = fetch_jobs_from_page(driver, job_number)
        all_jobs_data.extend(page_jobs)
        print(f"Scraped page {job_number//20 + 1}")
        time.sleep(2)  # Add a delay between pages

    driver.quit()
    return all_jobs_data

def main():
    jobs = fetch_all_jobs()
    
    json_output = json.dumps(jobs, indent=2, ensure_ascii=False)
    print(f"Total jobs scraped: {len(jobs)}")

    with open('data.json', 'w', encoding='utf-8') as f:
        f.write(json_output)

if __name__ == '__main__':
    main()