# LinkedIn Job Scraper – Student & Part-Time Developer Roles

This is a Python automation script that searches for relevant **software development jobs** on LinkedIn, filters them based on smart criteria, and updates a connected **Google Sheet** with only relevant results.

---

##  Features

-  Scrapes multiple LinkedIn job search URLs
-  Human-like scrolling and page behavior
-  Smart filtering: only part-time/student/junior jobs in development or automation
-  Avoids duplicates
-  Automatically deletes job posts older than 3 weeks
-  Google Sheets integration
-  Supports scheduled execution (every 3 hours or more)

---

## 🛠 Setup

### 1. Clone this repo

```bash
git clone https://github.com/danagoro1212/job-automation.git
cd job-automation
```

### 2. Create a virtual environment and activate it

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Google Sheets Setup
To enable writing job results to your own Google Sheet:

### Step 1 – Create a Google Cloud Project
Go to [Google Cloud Console](https://console.cloud.google.com/)

Create a new project

### Step 2 – Enable Google Sheets API
Navigate to **APIs & Services > Library**

Search for **Google Sheets API** and enable it

### Step 3 – Create a Service Account
Go to **IAM & Admin > Service Accounts**

Click **Create Service Account**

Download and save the generated JSON file

### Step 4 – Share your Google Sheet
Create a Google Sheet

Share it with the **service account email** (from the JSON file) with **Editor** permissions

### Step 5 – Add credentials
Copy `credentials.json.example` → `credentials.json`

Paste your actual service account content into `credentials.json`

## Configuration

In `linkedin_scraper.py`, update:

`CHROME_DRIVER_PATH` — path to your ChromeDriver binary

`CHROME_PROFILE_PATH` — your local Chrome profile with LinkedIn session

`SPREADSHEET_ID` — the ID of your Google Sheet

Add more URLs in `LINKEDIN_SEARCH_URLS` if needed

##  How to Run

### Run manually from terminal:

```bash
python linkedin_scraper.py
```

### Run via '.bat' file (Windows):

```bash
run_linkedin_scraper.bat
```

## Run Every 3 Hours (Optional)
Use **Windows Task Scheduler**:

Create a task to run `run_linkedin_scraper.bat`

Set trigger to run every 3 hours

Make sure it runs with your user and stays visible (CMD)

## .gitignore Includes

credentials.json

.env and logs

chromedriver*

__pycache__/

.pyc files

## Questions?
Open an issue or contact danagoro66@gmail.com
Feel free to fork and contribute!
