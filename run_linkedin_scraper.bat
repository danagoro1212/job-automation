@echo off
cd /d "C:\Users\Danag\source\repos\job-automation"
call venv\Scripts\activate
cmd /k python linkedin_scraper.py
