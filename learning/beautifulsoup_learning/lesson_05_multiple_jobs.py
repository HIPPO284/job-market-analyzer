import requests  # 发送 HTTP request
from bs4 import BeautifulSoup  # 解析 HTML
from urllib.parse import urljoin  # 组合 relative URL


def download_page(url):  # 负责下载一个页面
    response = requests.get(url, timeout=10)  # GET 当前 URL
    response.raise_for_status()  # 如果出现 HTTP error 就抛出异常
    return response.text  # 返回 HTML string


def get_text_or_none(tag):  # 安全提取文字
    if tag is not None:
        return tag.get_text(strip=True)  # Tag -> clean string
    return None  # Tag 不存在就返回 None


def parse_jobs(html, page_url):  # 从一页 HTML 中提取职位
    soup = BeautifulSoup(html, "html.parser")  # HTML -> soup

    job_cards = soup.select(".job-card")  # 找当前页面所有职位卡

    jobs = []  # 保存当前页面所有职位

    for card in job_cards:  # 一个一个处理职位卡

        title_tag = card.select_one(".job-title")  # 找职位名称
        company_tag = card.select_one(".company")  # 找公司
        location_tag = card.select_one(".location")  # 找地点
        link_tag = card.select_one(".job-link")  # 找职位链接

        title = get_text_or_none(title_tag)  # Tag -> string
        company = get_text_or_none(company_tag)  # Tag -> string
        location = get_text_or_none(location_tag)  # Tag -> string

        job_url = None  # 默认没有 URL

        if link_tag is not None:  # 确保 <a> 存在
            href = link_tag.get("href")  # 提取 href attribute

            if href is not None:
                job_url = urljoin(page_url, href)  # relative -> absolute URL

        job = {  # 标准化职位数据
            "title": title,
            "company": company,
            "location": location,
            "url": job_url
        }

        jobs.append(job)  # 加入当前页面的 jobs

    return jobs  # 返回当前页面的职位


def get_next_page(html, current_url):  # 找下一页 URL
    soup = BeautifulSoup(html, "html.parser")  # 解析当前页面

    next_link = soup.select_one(".next-page")  # 找 Next link

    if next_link is None:
        return None  # 没有 Next，说明已经最后一页

    href = next_link.get("href")  # 提取 href

    if href is None:
        return None  # 有标签但没有链接，也停止

    return urljoin(current_url, href)  # 得到下一页完整 URL


def scrape_all_jobs(start_url, max_pages=10):  # 多页爬虫
    all_jobs = []  # 保存所有页面的职位
    seen_urls = set()  # 保存已经出现过的 URL，用来去重

    current_url = start_url  # 第一页 URL
    page_number = 0  # 已经处理的页面数

    while current_url is not None and page_number < max_pages:

        html = download_page(current_url)  # 下载当前页面

        page_jobs = parse_jobs(html, current_url)  # 当前 HTML -> jobs

        for job in page_jobs:  # 把当前页职位加入总结果
            job_url = job["url"]

            if job_url is None or job_url not in seen_urls:
                all_jobs.append(job)  # 没重复才添加

                if job_url is not None:
                    seen_urls.add(job_url)  # 记录 URL

        current_url = get_next_page(html, current_url)  # 找下一页

        page_number += 1  # 当前页处理完成

    return all_jobs  # 返回全部职位