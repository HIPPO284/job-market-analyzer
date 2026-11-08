import requests  # 用来向网站发送 HTTP request
from bs4 import BeautifulSoup  # 用来解析 HTML
from urllib.parse import urljoin  # 用来组合 base URL 和 relative URL


def download_page(url):  # 这个 function 只负责 URL -> HTML

    response = requests.get(url, timeout=10)  # 发送 GET request，并设置 timeout

    response.raise_for_status()  # 如果出现 404 / 500 等 HTTP error，就抛出 exception

    return response.text  # 返回网页 HTML string


def get_text_or_none(tag):  # 安全地从 Tag 中提取文字

    if tag is not None:  # find() 找到元素时，tag 不会是 None
        return tag.get_text(strip=True)  # Tag -> clean string

    return None  # 如果网页没有这个字段，就返回 None


def get_url_or_none(link_tag, base_url):  # 安全地提取并整理 URL

    if link_tag is None:  # 如果根本没有 <a> Tag
        return None  # URL 数据不存在

    relative_url = link_tag.get("href")  # 提取 href attribute

    if relative_url is None:  # <a> 存在但没有 href
        return None

    return urljoin(base_url, relative_url)  # Relative URL -> Absolute URL


def parse_jobs(html, base_url):  # 这个 function 只负责 HTML -> jobs list

    soup = BeautifulSoup(html, "html.parser")  # HTML string -> BeautifulSoup object

    job_cards = soup.find_all(  # 找出网页中的所有职位卡片
        "article",
        class_="job-card"
    )

    jobs = []  # 最终所有职位都会放到这个 list 中

    for job_card in job_cards:  # 每次 loop 只处理一个职位

        title_tag = job_card.find(  # 找当前职位的 title
            "h2",
            class_="job-title"
        )

        company_tag = job_card.find(  # 找当前职位的 company
            "p",
            class_="company"
        )

        location_tag = job_card.find(  # 找当前职位的 location
            "p",
            class_="location"
        )

        salary_tag = job_card.find(  # salary 可能不存在
            "p",
            class_="salary"
        )

        link_tag = job_card.find(  # 找职位详情页面的 link
            "a",
            class_="job-link"
        )

        title = get_text_or_none(title_tag)  # Tag -> string / None
        company = get_text_or_none(company_tag)  # Tag -> string / None
        location = get_text_or_none(location_tag)  # Tag -> string / None
        salary = get_text_or_none(salary_tag)  # 缺失 salary 时得到 None

        job_url = get_url_or_none(link_tag, base_url)  # 提取并组合完整 URL

        job = {  # 把一个职位标准化成 dictionary
            "title": title,
            "company": company,
            "location": location,
            "salary": salary,
            "url": job_url
        }

        jobs.append(job)  # 把当前职位加入总 jobs list

    return jobs  # 返回 list of dictionaries


def scrape_jobs(url):  # 最外层 function：URL -> jobs list

    html = download_page(url)  # 第一步：下载 HTML

    jobs = parse_jobs(html, url)  # 第二步：解析 HTML

    return jobs  # 返回最终职位数据