from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json

def fetch_jobs_from_page(driver, job_number):
    url = f'https://www.rozee.pk/job/jsearch/q/all/fin/1/fpn/{job_number}'
    driver.get(url)

    wait = WebDriverWait(driver, 80)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'job')))

    job_elements = driver.find_elements(By.CLASS_NAME, 'job')
    
    print(f"Found {len(job_elements)} job elements on page {job_number//20 + 1}.")

    jobs_data = []

    for job in job_elements:
        job_data = {}
        try:
            # Title
            h3_tag = job.find_element(By.CLASS_NAME, 's-18')
            if h3_tag:
                job_data['title'] = h3_tag.get_attribute('title')

            # Company name
            company_name_element = job.find_element(By.CLASS_NAME, 'cname')
            if company_name_element:
                job_data['company'] = company_name_element.text.strip()

            # Description
            description = job.find_element(By.CLASS_NAME, 'jbody')
            if description:
                job_data['description'] = description.text.strip()

            # Posted date
            posted_on = job.find_element(By.CSS_SELECTOR, 'span[data-original-title="Posted On"]')
            if posted_on:
                job_data['posted_on'] = posted_on.text.strip()

            # Experience
            experience = job.find_element(By.CSS_SELECTOR, '.func-area-drn')
            if experience:
                job_data['experience'] = experience.text.strip()

            # Salary
            salary = job.find_element(By.CSS_SELECTOR, 'span[data-original-title="Offer Salary - PKR"] span')
            if salary:
                job_data['salary'] = salary.text.strip()

            jobs_data.append(job_data)
        except Exception as e:
            print(f"Error processing job: {e}")
    
    return jobs_data

def fetch_all_jobs():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    all_jobs_data = []
    
    for job_number in range(0, 481, 20):  # Goes up to 460
        page_jobs = fetch_jobs_from_page(driver, job_number)
        all_jobs_data.extend(page_jobs)
        print(f"Scraped page {job_number//20 + 1}")
    
    driver.quit()
    return all_jobs_data

def main():
    jobs = fetch_all_jobs()
    
    json_output = json.dumps(jobs, indent=2, ensure_ascii=False)
    print(f"Total jobs scraped: {len(jobs)}")

    with open('all_jobs_data.json', 'w', encoding='utf-8') as f:
        f.write(json_output)

if __name__ == '__main__':
    main()