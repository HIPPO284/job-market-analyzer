from datetime import datetime, timezone
from html import unescape

import requests
from bs4 import BeautifulSoup


API_URL = "https://api.lever.co/v0/postings/{company_name}"


def fetch_lever_jobs(company_name="leverdemo"):
    try:
        response = requests.get(
            API_URL.format(company_name=company_name),
            params={"mode": "json"},
            timeout=15,
        )
        response.raise_for_status()
        jobs = response.json()

        if not isinstance(jobs, list):
            raise ValueError("Lever response must be a jobs list")

    except (requests.RequestException, ValueError) as error:
        print(f"Could not download Lever jobs: {error}")
        return []

    return jobs


def clean_description(raw_html):
    decoded_html = unescape(raw_html or "")
    soup = BeautifulSoup(decoded_html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def date_from_milliseconds(value):
    try:
        return datetime.fromtimestamp(
            value / 1000, tz=timezone.utc
        ).date() if value else None
    except (TypeError, ValueError, OverflowError):
        return None


def parse_lever_jobs(jobs, company_name="leverdemo"):
    lever_jobs_list = []

    for job in jobs:
        categories = job.get("categories") or {}
        locations = categories.get("allLocations") or []

        if not locations and categories.get("location"):
            locations = [categories["location"]]

        location_list = []
        for location in locations:
            if isinstance(location, str) and location.strip():
                location_list.append({"city": location.strip(), "state": None, "country": None})

        lever_job = {}
        lever_job["source_name"] = "lever"
        lever_job["source_job_id"] = str(job["id"])
        lever_job["title"] = job.get("text")
        lever_job["company"] = company_name
        lever_job["location"] = location_list
        lever_job["workplace_type"] = None
        commitment = str(categories.get("commitment") or "").casefold()
        if "full time" in commitment or "full-time" in commitment:
            employment_type = "full_time"
        elif "part time" in commitment or "part-time" in commitment:
            employment_type = "part_time"
        elif "intern" in commitment:
            employment_type = "internship"
        elif "contract" in commitment:
            employment_type = "contract"
        elif "temporary" in commitment:
            employment_type = "temporary"
        else:
            employment_type = None
        lever_job["employment_type"] = employment_type
        lever_job["experience_level"] = None
        lever_job["salary_min"] = None
        lever_job["salary_max"] = None
        lever_job["salary_currency"] = None
        lever_job["salary_period"] = None
        lever_job["minimum_education_level"] = None
        lever_job["required_skills"] = []
        lever_job["preferred_skills"] = []
        lever_job["language_requirements"] = None
        lever_job["posted_date"] = date_from_milliseconds(job.get("createdAt"))
        lever_job["source_updated_at"] = None
        lever_job["application_deadline"] = None
        lever_job["application_url"] = job.get("hostedUrl") or job.get("applyUrl")
        lever_job["description_text"] = (
            job.get("descriptionPlain")
            or clean_description(job.get("description"))
        )
        lever_job["role_summary"] = None
        lever_job["raw_categories"] = categories
        lever_job["raw_lists"] = job.get("lists") or []

        lever_jobs_list.append(lever_job)

    return lever_jobs_list


if __name__ == "__main__":
    jobs = fetch_lever_jobs("leverdemo")
    lever_jobs = parse_lever_jobs(jobs, "leverdemo")

    for job in lever_jobs[:3]:
        print(job)

