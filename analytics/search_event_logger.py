import json
from datetime import datetime
from pathlib import Path    # process file safely
from uuid import uuid4      # create unique id for each search

SEARCH_EVENT_PATH = Path(__file__).with_name("search_events.jsonl")      # __file__ 是当前这个 Python 文件的路径


def first_or_none(values):
    if isinstance(values, list) and values:
        return values[0]
    return None


def append_search_event(user_preferences, search_result):
    event = {
        "event_id": str(uuid4()),
        "occurred_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "skill_ids": user_preferences.get("skill_ids", []),
        "skill_names": sorted(user_preferences.get("skills", [])),  #  JSON 无法直接保存 Python 的 set；排序后会变成 JSON 支持的列表
        "location": {
            "id": user_preferences.get("location_id"),
            "type": user_preferences.get("location_type"),
            "country_id": user_preferences.get("location_country_id"),
            "name": first_or_none(user_preferences.get("locations", [])),
        },
        "workplace_type": first_or_none(
            user_preferences.get("workplace_types", [])
        ),
        "experience_level": first_or_none(
            user_preferences.get("experience_levels", [])
        ),
        "employment_type": first_or_none(
            user_preferences.get("employment_types", [])
        ),
        "education_level": user_preferences.get("education_level"),
        "minimum_salary": user_preferences.get("minimum_salary"),
        "salary_currency": user_preferences.get("salary_currency"),
        "total_matched_count": search_result.get("total_matched_count", 0),
        "displayed_count": search_result.get("displayed_count", 0),
    }

    with SEARCH_EVENT_PATH.open("a", encoding="utf-8") as file:
        json.dump(event, file, ensure_ascii=False)
        file.write("\n")