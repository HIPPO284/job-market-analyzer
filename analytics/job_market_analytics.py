import json
from datetime import datetime
from pathlib import Path
from job_repository import get_all_jobs
from collections import Counter
import matplotlib.pyplot as plt
from database import get_database_connection


JOB_MARKET_ANALYTICS_PATH = Path(__file__).with_name("job_market_analytics.json")
WORKPLACE_CHART_PATH = Path(__file__).with_name("workplace_type_analytics_chart.png")
EMPLOYMENT_CHART_PATH = Path(__file__).with_name("employment_type_analytics_chart.png")
EXPERIENCE_CHART_PATH = Path(__file__).with_name("experience_level_analytics_chart.png")
SEARCH_ANALYTICS_PATH = Path(__file__).with_name("search_analytics.json")
SEARCH_EVENTS_PATH = Path(__file__).with_name("search_events.jsonl")

TEM_JOB_MARKET_ANALYTICS_PATH = Path(__file__).with_name("tem_job_market_analytics.json")
TEM_WORKPLACE_CHART_PATH = Path(__file__).with_name("tem_workplace_type_analytics_chart.png")
TEM_EMPLOYMENT_CHART_PATH = Path(__file__).with_name("tem_employment_type_analytics_chart.png")
TEM_EXPERIENCE_CHART_PATH = Path(__file__).with_name("tem_experience_level_analytics_chart.png")
TEM_SEARCH_ANALYTICS_PATH = Path(__file__).with_name("tem_search_analytics.json")


def save_pie_chart(counts, title, output_path):
    plt.figure(figsize=(4.5, 4.5))

    values = list(counts.values())
    total = sum(values)

    labels = []
    for name, count in counts.items():
        percentage = count / total * 100
        labels.append(f"{name}: {percentage:.1f}%")

    wedges, texts = plt.pie(
        values,
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2}
    )

    plt.title(title)
    plt.legend(wedges, labels,ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.05), fontsize=12)
    plt.axis("equal")
    plt.savefig(output_path, dpi=160, bbox_inches="tight", transparent=True)
    plt.close()



def build_job_market_analytics():
    jobs = get_all_jobs()
    total_jobs = len(jobs)    # 1
    company_counts = Counter()
    country_counts = Counter()
    skill_counts = Counter()
    workplace_counts = Counter()
    employment_counts = Counter()
    experience_counts = Counter()
    for job in jobs:
        company = job["company"]
        if company:
            company_counts[company] += 1
        job_country_ids = {location["country_id"] for location in job["locations"] if location["country_id"] is not None}
        job_skills = (set(job["required_skills"]) | set(job["preferred_skills"]))
        country_counts.update(job_country_ids)    # 2
        skill_counts.update(job_skills)    #  job_country_ids 是一个 set，不能作为 Counter 的 key  3

        workplace_options = {
            value.strip().lower()
            for value in (job["workplace_type"] or "").split(",")
            if value.strip()
        }

        if "hybrid" in workplace_options:
            workplace_type = "Hybrid"
        elif workplace_options == {"remote"}:
            workplace_type = "Remote"
        elif workplace_options == {"onsite"}:
            workplace_type = "Onsite"
        elif workplace_options == {"remote", "onsite"}:
            workplace_type = "Multiple options"
        else:
            workplace_type = "Not specified"

        employment_type = {
            "full_time": "Full-time",
            "part_time": "Part-time",
            "internship": "Internship",
            "contract": "Contract",
            "temporary": "Temporary"
        }.get(job["employment_type"], "Not specified")

        experience_level = {
            "entry": "Entry",
            "junior": "Junior",
            "intermediate": "Intermediate",
            "senior": "Senior"
        }.get(job["experience_level"], "Not specified")
        workplace_counts[workplace_type] += 1    # 4
        employment_counts[employment_type] += 1   # 5
        experience_counts[experience_level] += 1   # 6

    total_companies = len(company_counts)
    total_countries = len(country_counts)
    top_skills = skill_counts.most_common(5)
    top_skill_names = [skill_name for skill_name, count in top_skills]

    top_country_ids = country_counts.most_common(5)
    last_refreshed = datetime.now().astimezone().isoformat()
    save_pie_chart(workplace_counts, "Workplace Type", TEM_WORKPLACE_CHART_PATH)
    save_pie_chart(employment_counts, "Employment Type", TEM_EMPLOYMENT_CHART_PATH)
    save_pie_chart(experience_counts, "Experience Level", TEM_EXPERIENCE_CHART_PATH)

    TEM_WORKPLACE_CHART_PATH.replace(WORKPLACE_CHART_PATH)
    TEM_EMPLOYMENT_CHART_PATH.replace(EMPLOYMENT_CHART_PATH)
    TEM_EXPERIENCE_CHART_PATH.replace(EXPERIENCE_CHART_PATH)

    top_countries = []

    country_ids = [
        country_id
        for country_id, count in top_country_ids
    ]

    if country_ids:
        connection = get_database_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            placeholders = ", ".join(["%s"] * len(country_ids))

            cursor.execute(
                f"""
                SELECT geoname_id, name
                FROM locations
                WHERE location_type = 'country'
                  AND geoname_id IN ({placeholders})
                """,
                country_ids
            )
            country_rows = cursor.fetchall()

            for country_id, count in top_country_ids:
                for row in country_rows:
                    if row["geoname_id"] == country_id:
                        top_countries.append(row["name"])
                        break

            if len(top_countries) != len(country_ids):
                raise ValueError("Some country IDs have no matching country name.")

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    analytics_data = {
        "job_last_refreshed": last_refreshed,
        "overview": {
            "total_jobs": total_jobs,
            "companies": total_companies,
            "countries": total_countries,
        },
        "top_skills": top_skill_names,
        "top_countries": top_countries,

        "charts": {
            "workplace_type": WORKPLACE_CHART_PATH.name,
            "employment_type": EMPLOYMENT_CHART_PATH.name,
            "experience_level": EXPERIENCE_CHART_PATH.name,
        },
    }
    with TEM_JOB_MARKET_ANALYTICS_PATH.open("w", encoding="utf-8") as file:
        json.dump(analytics_data, file, ensure_ascii=False, indent=2)
    TEM_JOB_MARKET_ANALYTICS_PATH.replace(JOB_MARKET_ANALYTICS_PATH)



def build_search_analytics():
    search_count = 0
    search_skill_counts = Counter()
    preferred_country_counts = Counter()
    search_last_refreshed = None

    if not SEARCH_EVENTS_PATH.exists():
        if SEARCH_ANALYTICS_PATH.exists():
            return
        search_analytics_data = {
            "search_last_refreshed": None,
            "top_searched_skills": [],
            "top_preferred_countries": []
        }
        with TEM_SEARCH_ANALYTICS_PATH.open("w", encoding="utf-8") as file:
            json.dump(search_analytics_data, file, ensure_ascii=False, indent=2)
        TEM_SEARCH_ANALYTICS_PATH.replace(SEARCH_ANALYTICS_PATH)
        return

    with SEARCH_EVENTS_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            event = json.loads(line)
            search_count += 1
            search_last_refreshed = (event.get("occurred_at") or search_last_refreshed)

            searched_skills = set(event.get("skill_names", []))
            search_skill_counts.update(searched_skills)

            location = event.get("location") or {}
            country_id = location.get("country_id")
            if country_id is not None:
                preferred_country_counts[country_id] += 1

        top_preferred_country_ids = preferred_country_counts.most_common(5)

    top_countries = []
    country_ids = [country_id for country_id, count in top_preferred_country_ids]

    if country_ids:
        connection = get_database_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            placeholders = ", ".join(["%s"] * len(country_ids))

            cursor.execute(
                f"""
                    SELECT geoname_id, name
                    FROM locations
                    WHERE location_type = 'country'
                        AND geoname_id IN ({placeholders})
                    """,
                country_ids
            )
            country_rows = cursor.fetchall()

            for country_id, count in top_preferred_country_ids:
                for row in country_rows:
                    if row["geoname_id"] == country_id:
                        top_countries.append(row["name"])
                        break

            if len(top_countries) != len(country_ids):
                raise ValueError("Some country IDs have no matching country name.")

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    top_searched_skills = search_skill_counts.most_common(5)
    top_skill_names = [skill_name for skill_name, count in top_searched_skills]


    search_analytics_data = {
        "search_last_refreshed": search_last_refreshed,
        "top_searched_skills": top_skill_names,
        "top_preferred_countries": top_countries
    }
    if search_count >= 5:
        with TEM_SEARCH_ANALYTICS_PATH.open("w", encoding="utf-8") as file:
            json.dump(search_analytics_data, file, ensure_ascii=False, indent=2)
    else:
        search_analytics_data = {
            "search_last_refreshed": search_last_refreshed,
            "top_searched_skills": [],
            "top_preferred_countries": []
        }
        with TEM_SEARCH_ANALYTICS_PATH.open("w", encoding="utf-8") as file:
            json.dump(search_analytics_data, file, ensure_ascii=False, indent=2)

    TEM_SEARCH_ANALYTICS_PATH.replace(SEARCH_ANALYTICS_PATH)  #  Atomic File Replacement





if __name__ == "__main__":
    build_job_market_analytics()
    build_search_analytics()













