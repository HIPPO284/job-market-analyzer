from bs4 import BeautifulSoup  # 导入 BeautifulSoup，用来解析 HTML
from urllib.parse import urljoin  # Python 标准库，用来组合 URL，不需要 pip install


html = """
<section id="job-results">

    <article class="job-card">
        <h2 class="job-title">
            Junior Python Developer
        </h2>

        <p class="company">
            Maple Software
        </p>

        <p class="location">
            Edmonton, AB
        </p>

        <p class="salary">
            $65,000 - $75,000
        </p>

        <a class="job-link" href="/jobs/101">
            View Job
        </a>
    </article>


    <article class="job-card">
        <h2 class="job-title">
            Data Analyst Intern
        </h2>

        <p class="company">
            Northern Analytics
        </p>

        <p class="location">
            Calgary, AB
        </p>

        <a class="job-link" href="/jobs/102">
            View Job
        </a>
    </article>

</section>
"""


base_url = "https://jobs.example.com"  # 网站基础 URL

soup = BeautifulSoup(html, "html.parser")  # 把普通 HTML string 解析成 BeautifulSoup object

jobs_section = soup.select_one("#job-results")  # #job-results 表示寻找 id="job-results"

job_cards = jobs_section.select(".job-card")  # .job-card 表示 class="job-card"，select() 返回 list

jobs = []  # 创建空 list，之后存放每一个 job dictionary


for job_card in job_cards:  # 每次循环处理一个职位

    title_tag = job_card.select_one(".job-title")  # select_one() 找当前 card 中第一个 matching element

    company_tag = job_card.find("p", class_="company")  # find() 也可以按照 tag + class 查找

    location_tag = job_card.find("p", class_="location")  # 找 location 对应的 Tag

    salary_tag = job_card.find("p", class_="salary")  # 有些职位可能没有 salary，所以可能返回 None

    link_tag = job_card.find("a", class_="job-link")  # 找到 <a> Tag


    title = title_tag.get_text(strip=True)  # get_text() 提取文字，strip=True 清理前后空白

    company = company_tag.get_text(strip=True)  # Tag -> clean Python string

    location = location_tag.get_text(strip=True)  # 提取 location 文字


    if salary_tag is not None:  # find() 找不到东西时会返回 None
        salary = salary_tag.get_text(strip=True)  # 有 salary 就提取文字
    else:
        salary = None  # 缺失数据使用 None，不自己猜一个值

    relative_url = link_tag.get("href")  # .get("href") 提取 HTML attribute

    full_url = urljoin(base_url, relative_url)  # 把 relative URL 转成 absolute URL

    job = {  # 把当前职位的数据组成 dictionary
        "title": title,
        "company": company,
        "location": location,
        "salary": salary,
        "url": full_url
    }
    jobs.append(job)  # 把当前 dictionary 加进 jobs list
for job in jobs:  # 遍历最终得到的职位数据
    print("Title:", job["title"])
    print("Company:", job["company"])
    print("Location:", job["location"])
    print("Salary:", job["salary"])
    print("URL:", job["url"])
    print()