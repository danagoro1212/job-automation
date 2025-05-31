import time
import random
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sys

# === CONFIGURATION ===
CHROME_DRIVER_PATH = r"C:\Users\Danag\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
CHROME_PROFILE_PATH = r"C:\Users\Danag\Downloads\chromedriver-win64\linkedin_automation_profile"
LINKEDIN_SEARCH_URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=automation%20student&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=integration%20student&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=backend%20student&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=software%20student&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=developer%20part%20time&location=Israel",
    "https://www.linkedin.com/jobs/search/?keywords=fullstack%20student&location=Israel"
]

# === Filter function ===
def is_relevant(title: str, company: str, link: str) -> bool:
    text = f"{title.lower()} {company.lower()} {link.lower()}"
    relaxed_keywords = ["student", "intern", "part time", "חלקית", "סטודנט", "junior", "entry level"]
    dev_keywords = ["developer", "software", "backend", "fullstack", "automation", "integration", "engineer", "פיתוח"]
    forbidden = ["senior", "lead", "manager", "architect", "מנהל", "ראש צוות"]

    return (
        (any(word in text for word in relaxed_keywords) or any(word in text for word in dev_keywords))
        and not any(word in text for word in forbidden)
    )

# === Scroll inside job list container using custom selector ===
def scroll_inside_job_list(driver, max_scrolls=15):
    try:
        scrollable_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#main div.scaffold-layout__list-detail-inner--grow div.scaffold-layout__list > div"))
        )
        for _ in range(max_scrolls):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(random.uniform(1.2, 1.8))
    except Exception as e:
        print("⚠️ Failed to scroll inside job list:", e)

# === Go through pagination ===
def scrape_all_pages(driver, writer, seen_links):
    while True:
        scroll_inside_job_list(driver)
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card-container")
        print(f"🔎 Found {len(job_cards)} job cards")

        for job in job_cards:
            try:
                title_element = job.find_element(By.CSS_SELECTOR, "a.job-card-list__title--link")
                company_element = job.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__subtitle span")
                link = title_element.get_attribute("href")

                if link in seen_links:
                    continue

                title = title_element.text.strip()
                company = company_element.text.strip()

                if is_relevant(title, company, link):
                    print(f"🔹 {title} – {company}\n🔗 {link}\n")
                    writer.writerow([title, company, link])
                    seen_links.add(link)
            except Exception as e:
                print("⚠️ Failed to extract job info:", e)

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="View next page"]')
            if next_button.is_enabled():
                prev_url = driver.current_url
                driver.execute_script("arguments[0].click();", next_button)

                WebDriverWait(driver, 20).until(
                    lambda d: d.current_url != prev_url
                )
                WebDriverWait(driver, 20).until_not(
                    EC.presence_of_element_located((By.CLASS_NAME, "artdeco-loader"))
                )
                time.sleep(2)
            else:
                break
        except:
            break

# === Set up browser ===
service = Service(executable_path=CHROME_DRIVER_PATH)
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-features=ChromeWhatsNewUI")

driver = webdriver.Chrome(service=service, options=options)

# === Open LinkedIn and wait for login session ===
print("🌐 Opening browser and checking login status...")
driver.get("https://www.linkedin.com")

try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "global-nav-search"))
    )
    print("✅ Logged in successfully")
except:
    print("❌ Could not confirm login. Exiting.")
    driver.quit()
    exit()

# === Prepare CSV file and seen links ===
seen_links = set()
with open("linkedin_jobs.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Title", "Company", "Link"])

    for url in LINKEDIN_SEARCH_URLS:
        print(f"\n🌐 Navigating to: {url}")
        driver.get(url)

        success = False
        for attempt in range(3):
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-card-container"))
                )
                print("✅ Job cards detected. Beginning scroll and pagination...")
                scrape_all_pages(driver, writer, seen_links)
                success = True
                break
            except TimeoutException:
                print(f"⚠️ Attempt {attempt + 1} failed. Retrying in 8s...")
                time.sleep(8)
                driver.refresh()

        if not success:
            print("❌ Failed to load jobs after 3 attempts. Exiting script.")
            driver.quit()
            sys.exit()

driver.quit()
