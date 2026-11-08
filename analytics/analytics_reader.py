import json
from pathlib import Path
from datetime import datetime

JOB_MARKET_ANALYTICS_PATH = Path(__file__).with_name(
    "job_market_analytics.json"
)
SEARCH_ANALYTICS_PATH = Path(__file__).with_name(
    "search_analytics.json"
)

def load_analytics_data():
    with JOB_MARKET_ANALYTICS_PATH.open("r", encoding="utf-8") as file:
        job_data = json.load(file)

    job_data["job_last_refreshed"] = datetime.fromisoformat(job_data["job_last_refreshed"]).strftime("%Y-%m-%d")
                         #  把这个字符串解析成 Python 的 datetime 日期时间对象
    with SEARCH_ANALYTICS_PATH.open("r", encoding="utf-8") as file:
        search_data = json.load(file)

    return {
        "job": job_data,
        "search": search_data
    }