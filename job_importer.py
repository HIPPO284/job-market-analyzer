from jobs_data_ai_normalization import greenhouse_ai_normalizer, lever_ai_normalizer
from job_sources.greenhouse_source import fetch_greenhouse_jobs, parse_greenhouse_jobs
from job_sources.lever_source import fetch_lever_jobs, parse_lever_jobs
import requests
import json
from skill_normalizer import find_standard_skill
from database import get_database_connection
from pathlib import Path
from datetime import datetime

LOCATION_SEARCH_URL = "https://secure.geonames.org/searchJSON"
GEONAMES_PARAMS = {
    "username": "wukuncheng",
    "lang": "en",
    "style": "FULL",
    "maxRows": 8,
}


import unicodedata


COUNTRY_FEATURE_CODES = ("PCLI", "PCLS", "PCLD", "PCLF")


class GeoNamesQuotaExceeded(RuntimeError):
    """Raised when GeoNames reports that this account has exhausted a quota."""


def raise_if_geonames_quota_exceeded(data):
    """Stop an import batch instead of treating a quota response as no match."""
    if not isinstance(data, dict):
        return

    status = data.get("status")
    if not isinstance(status, dict):
        return

    value = status.get("value")
    message = str(status.get("message") or "")
    if value in (18, 19, 20) or "limit" in message.casefold() or "credit" in message.casefold():
        raise GeoNamesQuotaExceeded(
            f"GeoNames quota response ({value}): {message or 'quota limit reached'}"
        )


def search_country(country_name):
    params = GEONAMES_PARAMS.copy()
    params.update({
        "name_equals": country_name.strip(),
        "featureClass": "A",
        "featureCode": COUNTRY_FEATURE_CODES,
    })

    response = requests.get(
        LOCATION_SEARCH_URL,
        params=params,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def normalize_place_name(value):
    if not isinstance(value, str):
        return ""

    text = unicodedata.normalize("NFKD", value)

    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    return " ".join(
        text.casefold().replace("\u2019", "'").split()
    )


def valid_search_response(data):
    if not isinstance(data, dict):
        return False

    if "status" in data or "error" in data:
        return False

    rows = data.get("geonames")
    total = data.get("totalResultsCount")

    if (
        not isinstance(rows, list)
        or type(total) is not int
        or total < len(rows)
    ):
        return False

    for row in rows:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("name"), str)
        ):
            return False

        try:
            for key in ("geonameId", "countryId"):
                if (
                    isinstance(row.get(key), bool)
                    or int(row[key]) <= 0
                ):
                    return False

        except (KeyError, TypeError, ValueError, OverflowError):
            return False

    return True


def select_candidate(
    data,
    name,
    kind,
    country_code=None,
    province_code=None,
):
    if not isinstance(data, dict):
        return None

    if "status" in data or "error" in data:
        return None

    places = data.get("geonames")
    total = data.get("totalResultsCount")

    # 候选没有全部返回时，不从截断的结果中确定地址。
    if (
        not isinstance(places, list)
        or type(total) is not int
        or total != len(places)
    ):
        return None

    candidates = {}

    for place in places:
        if not isinstance(place, dict):
            return None

        try:
            if (
                isinstance(place.get("geonameId"), bool)
                or isinstance(place.get("countryId"), bool)
            ):
                return None

            geoname_id = int(place["geonameId"])
            country_id = int(place["countryId"])

            if (
                geoname_id <= 0
                or country_id <= 0
                or not isinstance(place.get("name"), str)
                or not place["name"].strip()
            ):
                return None

        except (KeyError, TypeError, ValueError, OverflowError):
            return None

        if (
            kind == "country"
            and place.get("fcode") not in COUNTRY_FEATURE_CODES
        ):
            continue

        if kind == "province" and place.get("fcode") != "ADM1":
            continue

        if kind == "city" and place.get("fcl") != "P":
            continue

        if country_code and place.get("countryCode") != country_code:
            continue

        if province_code and place.get("adminCode1") != province_code:
            continue

        candidates[geoname_id] = place

    if len(candidates) == 1:
        return next(iter(candidates.values()))

    matches = []
    query_name = normalize_place_name(name)

    for place in candidates.values():
        names = (
            normalize_place_name(place.get("name")),
            normalize_place_name(place.get("toponymName")),
        )

        if query_name and query_name in names:
            matches.append(place)

    if len(matches) == 1:
        return matches[0]

    return None


def job_location_selector(job):
    names = []
    locations = job.get("location")

    if not isinstance(locations, list):
        return names

    for location in locations:
        if not isinstance(location, dict):
            continue

        parts = []

        for key in ("city", "state", "country"):
            value = location.get(key)

            if isinstance(value, str) and value.strip():
                parts.append(value.strip())

        if parts:
            names.append(", ".join(parts))

    return names



def _unique_location_record(records):
    """Return one database record only when the match is unambiguous."""
    if len(records) != 1:
        return None
    return records[0].copy()


def load_location_cache():
    """Read known locations once so a batch can reuse existing GeoNames IDs."""
    cache = {
        "countries": {},
        "provinces": {},
        "cities_by_country": {},
        "cities_by_full_place": {},
    }

    connection = None
    cursor = None

    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                location.geoname_id,
                location.location_type,
                location.name,
                location.country_id,
                location.province_id,
                location.latitude,
                location.longitude,
                country.name AS country_name,
                province.name AS province_name
            FROM locations AS location
            LEFT JOIN locations AS country
                ON country.geoname_id = location.country_id
            LEFT JOIN locations AS province
                ON province.geoname_id = location.province_id
        """)
        rows = cursor.fetchall()

    except Exception as error:
        # A local-cache failure must not prevent the existing GeoNames fallback.
        print(f"Could not load local location cache: {error}")
        return cache

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

    for row in rows:
        record = {
            "geoname_id": row["geoname_id"],
            "location_type": row["location_type"],
            "name": row["name"],
            "country_id": row["country_id"],
            "province_id": row["province_id"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
        }
        country_name = normalize_place_name(row.get("country_name"))
        province_name = normalize_place_name(row.get("province_name"))
        place_name = normalize_place_name(record["name"])

        if record["location_type"] == "country":
            cache["countries"].setdefault(place_name, []).append(record)

        elif record["location_type"] == "province" and country_name:
            cache["provinces"].setdefault(
                (place_name, country_name), []
            ).append(record)

        elif record["location_type"] == "city" and country_name:
            cache["cities_by_country"].setdefault(
                (place_name, country_name), []
            ).append(record)

            if province_name:
                cache["cities_by_full_place"].setdefault(
                    (place_name, province_name, country_name), []
                ).append(record)

    return cache


def find_cached_location(location, cache):
    """Find an exact, unique place already saved in our locations table."""
    city = normalize_place_name(location.get("city"))
    state = normalize_place_name(location.get("state"))
    country = normalize_place_name(location.get("country"))

    if city and state and country:
        return _unique_location_record(
            cache["cities_by_full_place"].get((city, state, country), [])
        )

    if city and country:
        return _unique_location_record(
            cache["cities_by_country"].get((city, country), [])
        )

    if state and country:
        return _unique_location_record(
            cache["provinces"].get((state, country), [])
        )

    if country:
        return _unique_location_record(cache["countries"].get(country, []))

    return None

def location_id_search(merged_jobs):
    location_cache = load_location_cache()

    for job in merged_jobs:
        raw_locations = job.get("location")

        if raw_locations is None:
            continue

        if not isinstance(raw_locations, list):
            raw_locations = [raw_locations]
            job["location"] = raw_locations

        for index, raw_location in enumerate(raw_locations):
            if not isinstance(raw_location, dict):
                raw_location = {
                    "city": None,
                    "state": None,
                    "country": None,
                    "invalid_raw_location": raw_location,
                }
                raw_locations[index] = raw_location

            location = raw_location

            location["geonames_candidate"] = []
            location["geonames_total"] = None
            location["geonames_parent"] = None
            location["geonames_selected"] = None
            location["lookup_issue"] = None
            location["lookup_kind"] = None
            location["lookup_country_code"] = None
            location["lookup_province_code"] = None

            if "invalid_raw_location" in location:
                location["lookup_issue"] = "invalid_input"
                continue

            invalid_input = False

            for key in ("city", "state", "country"):
                value = location.get(key)

                if value is not None and not isinstance(value, str):
                    invalid_input = True

                location.setdefault(key, None)

            if invalid_input:
                location["lookup_issue"] = "invalid_input"
                continue

            cached_record = find_cached_location(location, location_cache)
            if cached_record is not None:
                location["location_record"] = cached_record
                location["lookup_source"] = "database"
                location["match_status"] = "resolved_from_database"
                location["match_precision"] = cached_record["location_type"]
                continue

            location["lookup_source"] = "geonames"
            country_code = None
            province_code = None

            try:
                # 先确认国家或地区。
                if normalize_place_name(location.get("country")):
                    data = search_country(location["country"])
                    raise_if_geonames_quota_exceeded(data)

                    if not valid_search_response(data):
                        location["lookup_issue"] = "country_lookup_failed"
                        continue

                    place = select_candidate(
                        data,
                        location["country"],
                        "country",
                    )

                    if place is None:
                        location["lookup_issue"] = "country_unresolved"
                        continue

                    country_code = place.get("countryCode")

                    if (
                        not isinstance(country_code, str)
                        or len(country_code) != 2
                    ):
                        location["lookup_issue"] = "invalid_country_response"
                        continue

                    location["geonames_parent"] = place

                # 有省份时，再确认省份。
                if normalize_place_name(location.get("state")):
                    data = search_province(
                        location["state"],
                        country_code,
                    )
                    raise_if_geonames_quota_exceeded(data)

                    if not valid_search_response(data):
                        location["lookup_issue"] = "province_lookup_failed"
                        continue

                    place = select_candidate(
                        data,
                        location["state"],
                        "province",
                        country_code,
                    )

                    if place is None:
                        location["lookup_issue"] = "province_unresolved"
                        continue

                    country_code = place.get("countryCode")
                    province_code = place.get("adminCode1")

                    location["geonames_parent"] = place

                location["lookup_country_code"] = country_code
                location["lookup_province_code"] = province_code

                # 有城市时，查询城市候选。
                if normalize_place_name(location.get("city")):
                    data = search_city(
                        location["city"],
                        country_code,
                        province_code,
                    )
                    raise_if_geonames_quota_exceeded(data)

                    location["lookup_kind"] = "city"

                    if not valid_search_response(data):
                        location["lookup_issue"] = "city_lookup_failed"
                        continue

                    location["geonames_candidate"] = data.get("geonames")
                    location["geonames_total"] = data.get("totalResultsCount")

                # 没有城市时，使用已经确认的省份或国家。
                elif location["geonames_parent"] is not None:
                    parent = location["geonames_parent"]

                    location["lookup_kind"] = (
                        "province"
                        if parent["fcode"] == "ADM1"
                        else "country"
                    )

                    location["geonames_candidate"] = [parent]
                    location["geonames_total"] = 1

                else:
                    location["lookup_issue"] = "empty_location"

            except (
                requests.exceptions.RequestException,
                ValueError,
                TypeError,
                KeyError,
                OverflowError,
            ):
                location["lookup_issue"] = "lookup_failed"

    return merged_jobs


def select_unique_location(location):
    issue = location.get("lookup_issue") or ""

    # 接口失败时返回 None，让现有保存逻辑保留旧关联。
    if issue.endswith("_failed") or issue == "invalid_country_response":
        location["match_status"] = "retry"
        location["match_precision"] = None
        return None

    kind = location.get("lookup_kind")

    query_key = {
        "city": "city",
        "province": "state",
        "country": "country",
    }.get(kind, "city")

    query = location.get(query_key)

    data = {
        "geonames": location.get("geonames_candidate"),
        "totalResultsCount": location.get("geonames_total"),
    }

    if kind:
        place = select_candidate(
            data,
            query,
            kind,
            location.get("lookup_country_code"),
            location.get("lookup_province_code"),
        )
    else:
        place = None

    if place is None:
        place = location.get("geonames_parent")

        location["match_status"] = (
            "parent_only" if place else "unresolved"
        )

        if kind == "city" and location.get("lookup_issue") is None:
            location["lookup_issue"] = "city_not_unique_or_missing"

    else:
        location["match_status"] = "resolved"

    if place:
        if not normalize_place_name(location.get("country")):
            location["country"] = place.get("countryName")

        # 有对应省份 ID，才补入省份名称。
        if (
            place.get("fcl") == "P"
            and place.get("adminId1")
            and not normalize_place_name(location.get("state"))
        ):
            location["state"] = place.get("adminName1")

        if place.get("fcode") in COUNTRY_FEATURE_CODES:
            location["match_precision"] = "country"

        elif place.get("fcode") == "ADM1":
            location["match_precision"] = "province"

        else:
            location["match_precision"] = "city"

    else:
        location["match_precision"] = None

    return place


def build_location_record(location):
    place = location.get("geonames_selected")

    if place is None:
        return None

    try:
        if place.get("fcode") in COUNTRY_FEATURE_CODES:
            location_type = "country"

        elif place.get("fcode") == "ADM1":
            location_type = "province"

        elif place.get("fcl") == "P":
            location_type = "city"

        else:
            return None

        return {
            "geoname_id": int(place["geonameId"]),
            "location_type": location_type,
            "name": place["name"],
            "country_id": int(place["countryId"]),
            "province_id": (
                int(place["adminId1"])
                if place.get("adminId1")
                else None
            ),
            "latitude": place.get("lat"),
            "longitude": place.get("lng"),
        }

    except (KeyError, TypeError, ValueError, OverflowError):
        return None

def merge_jobs(greenhouse_ai_output, greenhouse_sys_output):
    merged_jobs = []
    ai_index = {}
    for ai_job in greenhouse_ai_output:
        key = (ai_job["source_name"], ai_job["source_job_id"])
        ai_index[key] = ai_job
    for sys_job in greenhouse_sys_output:
        key = (sys_job["source_name"], sys_job["source_job_id"])
        ai_job = ai_index.get(key)                                # O(n + m)
        merged_job = sys_job.copy()
        merged_job["ai_normalization_success"] = ai_job is not None

        if ai_job is not None:
            for key, value in ai_job.items():
                if value is not None or key in ("preferred_skills", "required_skills"):
                    merged_job[key] = value

        merged_jobs.append(merged_job)
    return merged_jobs




def search_province(state_name, country_code):
    params = GEONAMES_PARAMS.copy()
    params.update({
        "name_equals": state_name.strip(),
        "country": country_code,
        "featureClass": "A",
        "featureCode": "ADM1",
    })

    response = requests.get(LOCATION_SEARCH_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()

def search_city(city_name, country_code, province_code=None):
    params = GEONAMES_PARAMS.copy()
    params.update({
        "name_equals": city_name.strip(),
        "country": country_code,
        "featureClass": "P",
        "adminCode1": province_code,
    })

    response = requests.get(LOCATION_SEARCH_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()



def save_location(cursor, record):
    if record is None:
        return

    sql = """
        INSERT INTO locations (
            geoname_id, location_type, name,
            country_id, province_id, latitude, longitude
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s) AS incoming
        ON DUPLICATE KEY UPDATE
            location_type = incoming.location_type,
            name = incoming.name,
            country_id = incoming.country_id,
            province_id = incoming.province_id,
            latitude = incoming.latitude,
            longitude = incoming.longitude;
    """

    values = (
        record["geoname_id"],
        record["location_type"],
        record["name"],
        record["country_id"],
        record["province_id"],
        record["latitude"],
        record["longitude"],
    )
    cursor.execute(sql, values)



def save_job(cursor, job):
    if job is None:
        return None

    location_text = "; ".join(job_location_selector(job))
    if not location_text:
        location_text = job.get("raw_location_text") or "Not specified"

    workplace_text = job.get("workplace_type")
    if isinstance(workplace_text, list):
        workplace_text = ", ".join(workplace_text) or None

    languages = job.get("language_requirements")
    language_text = (
        json.dumps(languages, ensure_ascii=False)
        if languages is not None
        else None
    )

    sql = """
          INSERT INTO jobs (company,
                            title,
                            location,
                            workplace_type,
                            employment_type,
                            experience_level,
                            salary_min,
                            salary_max,
                            minimum_education_level,
                            posted_date,
                            application_deadline,
                            application_url,
                            source_name,
                            source_job_id,
                            source_updated_at,
                            description_text,
                            language_requirements,
                            salary_currency,
                            salary_period,
                            working_hours_per_week,
                            working_days_per_week,
                            role_summary)
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) AS incoming
          """

    if job["ai_normalization_success"]:

        sql += """
            ON DUPLICATE KEY UPDATE
                company = incoming.company,
                title = incoming.title,
                location = incoming.location,
                workplace_type = incoming.workplace_type,
                employment_type = incoming.employment_type,
                experience_level = incoming.experience_level,
                salary_min = incoming.salary_min,
                salary_max = incoming.salary_max,
                minimum_education_level = incoming.minimum_education_level,
                posted_date = incoming.posted_date,
                application_deadline = incoming.application_deadline,
                application_url = incoming.application_url,
                source_name = incoming.source_name,
                source_job_id = incoming.source_job_id,
                source_updated_at = incoming.source_updated_at,
                description_text = incoming.description_text,
                language_requirements = incoming.language_requirements,
                salary_currency = incoming.salary_currency,
                salary_period = incoming.salary_period,
                working_hours_per_week = incoming.working_hours_per_week,
                working_days_per_week = incoming.working_days_per_week,
                role_summary = incoming.role_summary;
        """
    else:
        sql += """
            ON DUPLICATE KEY UPDATE
                company = incoming.company,
                title = incoming.title,
                posted_date = incoming.posted_date,
                application_deadline = incoming.application_deadline,
                application_url = incoming.application_url,
                source_updated_at = incoming.source_updated_at,
                description_text = incoming.description_text;
        """

    values = (
        job["company"],
        job["title"],
        location_text,
        workplace_text,
        job.get("employment_type"),
        job.get("experience_level"),
        job.get("salary_min"),
        job.get("salary_max"),
        job.get("minimum_education_level"),
        job.get("posted_date"),
        job.get("application_deadline"),
        job.get("application_url"),
        job["source_name"],
        str(job["source_job_id"]),
        job.get("source_updated_at"),
        job.get("description_text"),
        language_text,
        job.get("salary_currency"),
        job.get("salary_period"),
        job.get("working_hours_per_week"),
        job.get("working_days_per_week"),
        job.get("role_summary"),
    )

    cursor.execute(sql, values)

    cursor.execute(
        """
        SELECT job_id
        FROM jobs
        WHERE source_name = %s AND source_job_id = %s;
        """,
        (job["source_name"], str(job["source_job_id"])),
    )
    row = cursor.fetchone()
    return row[0]



def save_job_location(cursor, job_id, geoname_id):
    if job_id is None or geoname_id is None:
        return

    sql = """
        INSERT INTO job_locations (job_id, geoname_id)
        VALUES (%s, %s) AS incoming
        ON DUPLICATE KEY UPDATE
        job_id = incoming.job_id,
        geoname_id = incoming.geoname_id
    """

    values = (
        job_id,
        geoname_id,
    )

    cursor.execute(sql, values)




def save_job_skill(cursor, job_id, skill_text, skill_type):
    if job_id is None or not skill_text:
        return

    standard_skill = find_standard_skill(skill_text)

    if standard_skill is None:
        print(f"Unmatched skill: {skill_text}")
        return

    sql = """
        INSERT INTO job_skills (job_id, skill_id, skill_type)
        VALUES (%s, %s, %s) AS incoming
        ON DUPLICATE KEY UPDATE
        job_id = incoming.job_id,
        skill_id = incoming.skill_id,
        skill_type = incoming.skill_type
    """

    values = (
        job_id,
        standard_skill["skill_id"],
        skill_type,
    )

    cursor.execute(sql, values)


def save_jobs(merged_jobs):
    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        for job in merged_jobs:
            job_id = save_job(cursor, job)
            if job["ai_normalization_success"]:
                locations_ready = job["location"] is not None

                for location in job["location"] or []:
                    if location["location_record"] is None:
                        locations_ready = False
                        break
                if locations_ready:
                    sql = """
                        DELETE FROM job_locations WHERE job_id = %s
                    """
                    cursor.execute(sql, (job_id,))
                    for location in job["location"] or []:
                        record = location["location_record"]
                        save_location(cursor, record)
                        save_job_location(cursor, job_id, record["geoname_id"])

                required_ready = job["required_skills"] is not None

                for skill_text in job["required_skills"] or []:
                    if not find_standard_skill(skill_text):
                        required_ready = False
                        print(f"Unmatched required skill: {skill_text}")

                if required_ready:
                    cursor.execute(
                        "DELETE FROM job_skills WHERE job_id = %s AND skill_type = %s",
                        (job_id, "required"),
                    )
                    for skill_text in job["required_skills"]:
                        save_job_skill(cursor, job_id, skill_text, "required")

                preferred_ready = job["preferred_skills"] is not None

                for skill_text in job["preferred_skills"] or []:
                    if not find_standard_skill(skill_text):
                        preferred_ready = False
                        print(f"Unmatched preferred skill: {skill_text}")

                if preferred_ready:
                    cursor.execute(
                        "DELETE FROM job_skills WHERE job_id = %s AND skill_type = %s",
                        (job_id, "preferred"),
                    )
                    for skill_text in job["preferred_skills"]:
                        save_job_skill(cursor, job_id, skill_text, "preferred")

        connection.commit()

    except Exception:
        connection.rollback()    #如果保存中途报错，撤回尚未提交的数据库修改
        raise

    finally:
        cursor.close()
        connection.close()


def prepare_lever_jobs(company_name="leverdemo", limit=None):
    """Fetch and normalize Lever jobs without writing to the database."""
    raw_jobs = fetch_lever_jobs(company_name)
    if limit is not None:
        raw_jobs = raw_jobs[:limit]
    return lever_ai_normalizer(raw_jobs, company_name=company_name)



if __name__ == "__main__":
    company_name = "leverdemo"   # 改成真实 Lever 公司名
    limit = 10                    # 先测试 10 条

    lever_jobs = prepare_lever_jobs(
        company_name=company_name,
        limit=limit,
    )

    lever_jobs = location_id_search(lever_jobs)

    for job in lever_jobs:
        for location in job.get("location") or []:
            location["geonames_selected"] = select_unique_location(location)
            location["location_record"] = build_location_record(location)

    output_path = Path(__file__).with_name(
        f"lever_{company_name}_{datetime.now():%Y%m%d_%H%M%S}.json"
    )

    output_path.write_text(
        json.dumps(
            lever_jobs,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(f"Saved {len(lever_jobs)} Lever jobs to: {output_path}")

    save_jobs(lever_jobs)

"""
if __name__ == "__main__":
    use_saved_json = True

    if use_saved_json:
        input_path = Path(__file__).parent / "greenhouse_output_20261009_154922.json"
        merged_jobs = json.loads(
            input_path.read_text(encoding="utf-8")
        )
    else:
        green_jobs = fetch_greenhouse_jobs()[:150]
        print(f"Processing {len(green_jobs)} jobs")
        greenhouse_sys_output = parse_greenhouse_jobs(green_jobs)
        greenhouse_ai_output = greenhouse_ai_normalizer(green_jobs)
        merged_jobs = merge_jobs(
            greenhouse_ai_output, greenhouse_sys_output
        )
        merged_jobs = location_id_search(merged_jobs)

        for job in merged_jobs:
            for location in job["location"] or []:
                location["geonames_selected"] = select_unique_location(location)
                location["location_record"] = build_location_record(location)
    output_path = Path(__file__).with_name(
        f"greenhouse_output_{datetime.now():%Y%m%d_%H%M%S}.json"
    )

    output_path.write_text(
        json.dumps(
            merged_jobs,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(f"Saved {len(merged_jobs)} jobs to: {output_path}")

    save_jobs(merged_jobs)
"""