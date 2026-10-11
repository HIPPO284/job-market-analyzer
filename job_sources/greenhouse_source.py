import time
import requests
from html import unescape
from bs4 import BeautifulSoup
from datetime import date
import json


API_URL = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"

def fetch_greenhouse_jobs(board_token="stripe"):
    try:
        response = requests.get(API_URL.format(board_token=board_token), timeout=15)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            raise ValueError("Greenhouse response must contain a jobs list")

    except (requests.RequestException, ValueError) as error:
        print(f"Could not download Greenhouse jobs: {error}")
        return []

    return data["jobs"]

def clean_description(raw_html):
    decoded_html = unescape(raw_html or "")
    soup = BeautifulSoup(decoded_html, "html.parser")

    return soup.get_text(separator="\n", strip=True)


def parse_greenhouse_jobs(jobs):
    greenhouse_jobs_list = []
    for job in jobs:
        greenhouse_job = {}
        greenhouse_job["source_name"] = "greenhouse"
        greenhouse_job["source_job_id"] = job["id"]
        greenhouse_job["title"] = job["title"]
        greenhouse_job["company"] = job["company_name"]
        greenhouse_job["location"] = None
        greenhouse_job["workplace_type"] = None
        greenhouse_job["employment_type"] = None
        greenhouse_job["experience_level"] = None
        greenhouse_job["salary_min"] = None
        greenhouse_job["salary_max"] = None
        greenhouse_job["minimum_education_level"] = None
        greenhouse_job["required_skills"] = []
        greenhouse_job["preferred_skills"] = []
        greenhouse_job["posted_date"] = (job["first_published"][:10] if job["first_published"] else None)
        greenhouse_job["source_updated_at"] = (job["updated_at"][:10] if job["updated_at"] else None)
        ddl = job.get("application_deadline")
        ddl = (date.fromisoformat(ddl[:10]) if ddl else None)
        greenhouse_job["application_deadline"] = ddl
        greenhouse_job["application_url"] = job["absolute_url"]
        greenhouse_job["description_text"] = clean_description(job["content"])
        greenhouse_job["raw_offices"] = job.get("offices", [])
        greenhouse_job["raw_location_text"] = job["location"]["name"]
        greenhouse_jobs_list.append(greenhouse_job)
    return greenhouse_jobs_list


def ai_insert_info(job):
    ai_insert = {}
    ai_insert["description_text"] = clean_description(job["content"])
    ai_insert["offices"] = job["offices"]
    ai_insert["location"] = job["location"]["name"]
    return ai_insert





if __name__ == "__main__":
    jobs = fetch_greenhouse_jobs()
    greenhouse_jobs = parse_greenhouse_jobs(jobs)

    for job in greenhouse_jobs[:3]:
        print(job)

    if jobs:
        print(ai_insert_info(jobs[0]))

