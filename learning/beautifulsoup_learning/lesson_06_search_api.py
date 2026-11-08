import requests  # 用于向 Search API 发送 HTTP request


API_URL = "https://api.search.brave.com/res/v1/web/search"  # Search API endpoint


def search_jobs(query, api_key, count=5):  # 搜索关键词 -> 标准化搜索结果

    headers = {
        "X-Subscription-Token": api_key  # 把 API key 放进 request header
    }

    params = {
        "q": query,  # 搜索关键词
        "count": count,  # 最多返回多少个结果
        "country": "CA",  # 优先加拿大搜索结果
        "search_lang": "en"  # 搜索语言为 English
    }

    response = requests.get(
        API_URL,
        headers=headers,
        params=params,
        timeout=10
    )  # 向 Search API 发送 GET request

    response.raise_for_status()  # 如果出现 4xx / 5xx HTTP error，就抛出 exception

    data = response.json()  # JSON response -> Python dictionary

    web_data = data.get("web")  # 取得 web search 部分

    if web_data is None:
        return []  # 如果没有 web results，就返回空 list

    raw_results = web_data.get("results", [])  # 取得原始 search results list

    search_results = []  # 保存我们标准化后的结果

    for result in raw_results:  # 一次处理一个 search result

        title = result.get("title")  # 取得网页标题

        url = result.get("url")  # 取得网页 URL

        description = result.get("description")  # 取得搜索摘要


        search_result = {  # 统一成我们自己的 dictionary 格式
            "title": title,
            "url": url,
            "description": description
        }

        search_results.append(search_result)  # 加入最终结果 list

    return search_results  # 返回 list of dictionaries


api_key = "YOUR_API_KEY"  # 学习阶段可以这样写，正式项目以后改成环境变量


skills = ["Python", "SQL"]  # 假设用户填写的 skills

location = "Edmonton"  # 假设用户填写的 location

job_type = "internship"  # 假设用户选择 internship


query = f"{' '.join(skills)} {job_type} {location} Canada"  # 自动生成搜索关键词


results = search_jobs(
    query,
    api_key,
    count=5
)  # 调用我们自己的 search function


for result in results:  # 遍历标准化后的搜索结果
    print("Title:", result["title"])
    print("URL:", result["url"])
    print("Description:", result["description"])
    print()