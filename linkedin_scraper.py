import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# === CONFIGURATION ===
CHROME_DRIVER_PATH = r"C:\\Users\\Danag\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
CHROME_PROFILE_PATH = r"C:\\Users\\Danag\\Downloads\\chromedriver-win64\\linkedin_automation_profile"
LINKEDIN_SEARCH_URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=automation%20student&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=integration%20student&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=backend%20student&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=software%20student&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=developer%20part%20time&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=fullstack%20student&location=Israel"
]
SPREADSHEET_ID = "12KqzusLQn9lubHIEPgDa7b2fkFjo0fyVco0oPbVJxLw"
SHEET_NAME = "גיליון1"
CREDS_PATH = r"C:\\Users\\Danag\\Downloads\\chromedriver-win64\\job-hunting-automation-461510-e991504f4f81.json"

# === Filter function ===
def is_relevant(title: str, company: str, link: str) -> bool:
    text = f"{title.lower()} {company.lower()} {link.lower()}"
    relaxed_keywords = ["student", "intern", "part time", "חלקית", "סטודנט", "junior", "entry level"]
    dev_keywords = ["developer", "software", "backend", "fullstack", "automation", "integration", "engineer", "פיתוח"]
    forbidden = ["senior", "lead", "manager", "architect", "מנהל", "ראש צוות", "צפון", "haifa", "nahariya", "kiryat", "afula"]

    relevant_score = sum(word in text for word in relaxed_keywords) + sum(word in text for word in dev_keywords)
    is_blocked = any(word in text for word in forbidden)

    return relevant_score >= 2 and not is_blocked

# === Google Sheets Setup ===
def append_jobs_to_google_sheet(jobs):
    creds = Credentials.from_service_account_file(CREDS_PATH, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    existing = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A2:D").execute().get("values", [])
    existing_links = set(row[2] for row in existing if len(row) > 2)

    today = datetime.now()
    new_existing = [row for row in existing if len(row) < 4 or (today - datetime.strptime(row[3], "%Y-%m-%d")).days <= 21]
    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A2:D").execute()
    if new_existing:
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A2",
            valueInputOption="RAW",
            body={"values": new_existing}
        ).execute()

    rows_to_add = []
    for job in jobs:
        if job[2] not in existing_links:
            print(f"✅ Added to sheet: {job[0]} – {job[1]}")
            rows_to_add.append(job + [today.strftime("%Y-%m-%d")])

    if rows_to_add:
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1",
            valueInputOption="RAW",
            body={"values": rows_to_add}
        ).execute()

# === Scroll inside job list container ===
def scroll_inside_job_list(driver, max_scrolls=15):
    try:
        scrollable_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#main > div > div.scaffold-layout__list-detail-inner.scaffold-layout__list-detail-inner--grow > div.scaffold-layout__list > div"))
        )
        for _ in range(max_scrolls):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(random.uniform(0.6, 1.0))
    except Exception as e:
        pass

# === Scrape multiple pages ===
def scrape_pages(driver):
    all_jobs = []
    pages_scraped = 0
    max_pages = 5

    while pages_scraped < max_pages:
        scroll_inside_job_list(driver)
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
        for job in job_cards:
            try:
                title_element = job.find_element(By.XPATH, ".//a[contains(@class, 'job-card-list__title')]")
                company_element = job.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__subtitle span")
                link = title_element.get_attribute("href")
                title = title_element.text.strip()
                company = company_element.text.strip()
                if is_relevant(title, company, link):
                    all_jobs.append([title, company, link])
            except:
                continue

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="View next page"]')
            if next_button.is_enabled():
                driver.execute_script("arguments[0].click();", next_button)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-card-container"))
                )
                pages_scraped += 1
                time.sleep(2)
            else:
                break
        except:
            break

    return all_jobs

# === Main ===
def run():
    service = Service(executable_path=CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=service, options=options)

    all_results = []
    for url in LINKEDIN_SEARCH_URLS:
        driver.get(url)
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "job-card-container")))
            jobs = scrape_pages(driver)
            all_results.extend(jobs)
        except:
            continue

    append_jobs_to_google_sheet(all_results)
    driver.quit()

if __name__ == "__main__":
    run()
