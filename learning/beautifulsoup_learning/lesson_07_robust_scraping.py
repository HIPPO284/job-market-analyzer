import time  # 用于控制 request 速度

import requests  # HTTP requests
from bs4 import BeautifulSoup  # HTML parsing


HEADERS = {
    "User-Agent": "Mozilla/5.0"  # 给 request 添加基本 User-Agent
}


def download_page(url):

    try:  # 网络操作可能失败

        response = requests.get(
            url,
            headers=HEADERS,  # 添加 request headers
            timeout=10  # 防止程序无限等待
        )

        response.raise_for_status()  # 4xx / 5xx -> HTTPError

        return response.text  # 成功时返回 HTML

    except requests.exceptions.Timeout:
        print("Request timed out.")  # 请求超时

    except requests.exceptions.HTTPError as error:
        print("HTTP error:", error)  # 403 / 404 / 500 等

    except requests.exceptions.RequestException as error:
        print("Request error:", error)  # 其他 requests 网络错误

    return None  # 请求失败统一返回 None


def parse_jobs(html):

    soup = BeautifulSoup(html, "html.parser")  # HTML -> soup

    job_cards = soup.select(".job-card")  # 找所有职位

    jobs = []

    for card in job_cards:

        title_tag = card.select_one(".title")  # 找 title
        company_tag = card.select_one(".company")  # 找 company

        title = None
        company = None

        if title_tag is not None:
            title = title_tag.get_text(strip=True)  # 安全提取 title

        if company_tag is not None:
            company = company_tag.get_text(strip=True)  # 安全提取 company

        job = {
            "title": title,
            "company": company
        }

        jobs.append(job)

    return jobs


def scrape_pages(urls):

    all_jobs = []

    for url in urls:

        html = download_page(url)  # 下载当前页面

        if html is not None:  # request 成功才 parse
            jobs = parse_jobs(html)

            all_jobs.extend(jobs)  # 合并当前页面 jobs

        time.sleep(1)  # 每次 request 后暂停，避免请求过快

    return all_jobs