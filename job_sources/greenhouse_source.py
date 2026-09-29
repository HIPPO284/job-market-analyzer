import time
import requests
from html import unescape
from bs4 import BeautifulSoup

API_URL = "https://boards-api.greenhouse.io/v1/boards/cloudflare/jobs?content=true"

def fetch_greenhouse_jobs():
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Could not download Greenhouse jobs: {error}")
        return []

    data = response.json()
    return data["jobs"]

jobs = fetch_greenhouse_jobs()

def clean_description(raw_html):
    decoded_html = unescape(raw_html or "")
    soup = BeautifulSoup(decoded_html, "html.parser")

    return soup.get_text(separator="\n", strip=True)

greenhouse_jobs_list = []
def parse_greenhouse_jobs(jobs):
    for job in jobs:
        greenhouse_job = {}
        greenhouse_job["source_name"] = "greenhouse"
        greenhouse_job["source_job_id"] = job["id"]
        greenhouse_job["title"] = job["title"]
        greenhouse_job["company"] = job["company_name"]
        greenhouse_job["location"] = job["offices"][0]["location"]
        greenhouse_job["workplace_type"] = job["location"]["name"]
        greenhouse_job["employment_type"] = None
        greenhouse_job["experience_level"] = None
        greenhouse_job["salary_min"] = None
        greenhouse_job["salary_max"] = None
        greenhouse_job["minimum_education_level"] = None
        greenhouse_job["required_skills"] = []
        greenhouse_job["preferred_skills"] = []
        greenhouse_job["posted_date"] = (job["first_published"][:10] if job["first_published"] else None)
        greenhouse_job["source_updated_at"] = (job["updated_at"][:10] if job["updated_at"] else None)
        greenhouse_job["application_deadline"] = (job["application_deadline"][:10] if job["application_deadline"] else None)
        greenhouse_job["application_url"] = job["absolute_url"]
        greenhouse_job["description_text"] = clean_description(job["content"])
        greenhouse_jobs_list.append(greenhouse_job)
    return greenhouse_jobs_list
greenhouse_jobs = parse_greenhouse_jobs(jobs)

if __name__ == "__main__":
    for i in range(10):
        print(greenhouse_jobs[i])



