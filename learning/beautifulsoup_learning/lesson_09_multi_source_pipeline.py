def search_web(query):  # Search API：负责发现网页 URL
    return [
        {
            "title": "Python Developer",
            "url": "https://company-a.com/jobs/101"
        },
        {
            "title": "Data Analyst",
            "url": "https://company-b.com/jobs/202"
        }
    ]


def search_job_api(query):  # Job API：直接返回结构化职位
    return [
        {
            "title": "Backend Developer",
            "company": "Maple Tech",
            "location": "Edmonton",
            "salary_min": 70000,
            "salary_max": 85000,
            "url": "https://jobs.example.com/303",
            "source": "job_api"
        }
    ]


def parse_company_a(url):  # Website A 专用 scraper
    return {
        "title": "Python Developer",
        "company": "Company A",
        "location": "Edmonton",
        "salary_min": None,
        "salary_max": None,
        "url": url,
        "source": "company_a"
    }


def parse_company_b(url):  # Website B 专用 scraper
    return {
        "title": "Data Analyst",
        "company": "Company B",
        "location": "Calgary",
        "salary_min": 60000,
        "salary_max": 75000,
        "url": url,
        "source": "company_b"
    }


def scrape_search_result(result):  # 根据 URL 判断使用哪个 parser

    url = result["url"]

    if "company-a.com" in url:
        return parse_company_a(url)

    if "company-b.com" in url:
        return parse_company_b(url)

    return None  # 没有对应 parser 时暂时跳过


def deduplicate_jobs(jobs):  # 根据 URL 去重

    unique_jobs = []
    seen_urls = set()

    for job in jobs:

        url = job["url"]

        if url not in seen_urls:
            unique_jobs.append(job)
            seen_urls.add(url)

    return unique_jobs


def collect_jobs(query):  # 整个 multi-source pipeline

    all_jobs = []

    api_jobs = search_job_api(query)  # 从 Job API 获取职位
    all_jobs.extend(api_jobs)

    search_results = search_web(query)  # 从 Search API 获取 URLs

    for result in search_results:

        job = scrape_search_result(result)  # URL -> 对应 website scraper

        if job is not None:
            all_jobs.append(job)

    all_jobs = deduplicate_jobs(all_jobs)  # 最后统一去重

    return all_jobs


query = "Python SQL internship Edmonton"

jobs = collect_jobs(query)

for job in jobs:
    print(job)