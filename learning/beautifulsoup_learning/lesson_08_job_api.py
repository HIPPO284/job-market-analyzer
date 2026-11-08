import requests  # 调用 Job API


API_URL = "https://api.example.com/jobs"  # 假设的 Job API endpoint


def search_job_api(query, location):

    params = {
        "query": query,  # 职位搜索关键词
        "location": location  # 搜索地点
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=10
    )  # 向 Job API 发送 request

    response.raise_for_status()  # 检查 HTTP error

    data = response.json()  # JSON -> Python dictionary

    raw_jobs = data.get("results", [])  # API 原始职位 list

    jobs = []  # 保存标准化后的职位

    for raw_job in raw_jobs:

        job = {
            "title": raw_job.get("job_title"),  # API 字段 -> 自己的字段
            "company": raw_job.get("company_name"),
            "location": raw_job.get("location"),
            "salary_min": raw_job.get("salary_min"),
            "salary_max": raw_job.get("salary_max"),
            "url": raw_job.get("job_url")
        }

        jobs.append(job)  # 加入标准化 jobs list

    return jobs


jobs = search_job_api(
    "Python Developer",
    "Edmonton"
)


for job in jobs:
    print(job)