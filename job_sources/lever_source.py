import requests

API_URL = "https://api.lever.co/v0/postings/leverdemo"

params = {
    "mode": "json",
    "limit": 3,
}

def fetch_lever_jobs():
    try:
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        jobs = response.json()
        if not isinstance(jobs, list):
            raise ValueError("Lever response must be a jobs list")
    except (requests.RequestException, ValueError) as error:
        print(f"Could not download Lever jobs: {error}")
        return []

    return jobs