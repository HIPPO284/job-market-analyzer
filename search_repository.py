"""SQL 搜索通路：校验偏好 → SQL 筛选及评分 → 取前 100 个职位详情。

本次修正（2026-10-21）：必选技能的明确报错；多选条件；汇率缓存校验；地点国家门槛；
同一只读快照内取排名和详情；现有页面的 Overall Match Score 改为总分。
保留约定：技能 40% + 地点 60%，Top 100，薪资比较职位的最低年薪。
Remote 仍按既定产品规则不限制国家，不代表已核验签证/远程办公资格。
"""
import json
import logging
import math
import re
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit
import mysql.connector
from database import get_database_connection


RESULT_DISPLAY_LIMIT = 100
MAX_SELECTED_SKILLS = 50
MAX_EXCHANGE_RATE_AGE_DAYS = 7  # 留出周末/假日窗口，拒绝无限期使用旧汇率
MAX_CACHED_CURRENCIES = 256
WORKPLACE_TYPES = {"remote", "onsite", "hybrid"}
EDUCATION_RANKS = {
    "high_school_or_below": 0,
    "bachelor": 1,
    "master": 2,
    "doctoral": 3,
}
# 与地图已约定的展示分组一致：GeoNames 中国/香港/澳门/台湾 ID。
CHINA_COUNTRY_ID = 1814991
CHINA_GROUP_IDS = {1814991, 1819730, 1821275, 1668284}
logger = logging.getLogger(__name__)
EMPLOYMENT_TYPE_MATCHES = {
    "internship": ("internship",),
    "full_time": ("full_time", "contract", "temporary"),
    "part_time": ("part_time", "contract", "temporary"),
}
EXCHANGE_RATE_CACHE_PATH = (
    Path(__file__).parent / "currency" / "exchange_rates_cache.json"
)


def load_cached_exchange_rates():
    """1 EUR = rate 单位 quote，因此 quote 金额除以 rate 才是 EUR。"""
    try:
        if EXCHANGE_RATE_CACHE_PATH.stat().st_size > 256 * 1024:
            raise ValueError("Exchange-rate cache is too large.")
        with EXCHANGE_RATE_CACHE_PATH.open(encoding="utf-8") as file:
            cached_rates = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            "Exchange-rate cache is unavailable. "
            "Run currency/refresh_exchange_rate.py before searching by salary."
        ) from error

    if not isinstance(cached_rates, list) or not 1 <= len(cached_rates) <= MAX_CACHED_CURRENCIES:
        raise ValueError("Exchange-rate cache has an unexpected format.")

    rates_by_currency = {"EUR": 1.0}
    seen = set()
    today = datetime.now(timezone.utc).date()
    for rate_record in cached_rates:
        if not isinstance(rate_record, dict):
            raise ValueError("Exchange-rate cache contains an invalid record.")

        currency = rate_record.get("quote")
        rate = rate_record.get("rate")
        if not (
            isinstance(currency, str)
            and re.fullmatch(r"[A-Z]{3}", currency)
            and rate_record.get("base") == "EUR"
            and isinstance(rate, (int, float))
            and not isinstance(rate, bool)
            and 1e-9 <= rate <= 1e9
            and math.isfinite(rate)
            and rate > 0
        ):
            raise ValueError("Exchange-rate cache must contain valid EUR-based rates.")
        if currency in seen or (currency == "EUR" and rate != 1):
            raise ValueError("Exchange-rate cache contains duplicate or inconsistent rates.")
        try:
            rate_date = date.fromisoformat(rate_record["date"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Exchange-rate cache has an invalid date.") from error
        if not 0 <= (today - rate_date).days <= MAX_EXCHANGE_RATE_AGE_DAYS:
            raise ValueError(
                "Exchange-rate cache is stale or future-dated. "
                "Run currency/refresh_exchange_rate.py before searching by salary."
            )
        seen.add(currency)
        rates_by_currency[currency] = float(rate)

    return rates_by_currency


def _positive_id(value, field):
    if isinstance(value, bool) or not (
        isinstance(value, int)
        or isinstance(value, str) and re.fullmatch(r"[0-9]{1,10}", value)
    ):
        raise ValueError(f"Invalid {field}.")
    value = int(value)
    if not 0 < value <= 2**31 - 1:
        raise ValueError(f"Invalid {field}.")
    return value


def _choices(values, allowed, field):
    """多选用 OR；去重后不再悄悄丢弃第二个选项。"""
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, (list, tuple, set, frozenset)):
        raise ValueError(f"Invalid {field}.")
    selected = set()
    for value in values:
        if value is None or value == "":
            continue
        if not isinstance(value, str):
            raise ValueError(f"Invalid {field}.")
        value = value.strip().lower()
        if not value:
            continue
        if value not in allowed:
            raise ValueError(f"Invalid {field}: {value}")
        selected.add(value)
    return sorted(selected)


def _country_group(country_id):
    return CHINA_COUNTRY_ID if country_id in CHINA_GROUP_IDS else country_id


def search_jobs(user_preferences):
    """一次排名查询 + 批量详情查询；无效偏好抛 ValueError，由路由显示错误。"""
    if not isinstance(user_preferences, dict):
        raise ValueError("User preferences must be a dictionary.")
    raw_skill_ids = user_preferences.get("skill_ids") or []
    if not isinstance(raw_skill_ids, (list, tuple, set, frozenset)):
        raise ValueError("Skill IDs must be a list.")
    if not raw_skill_ids:
        # 这是既定输入规则，不能改成无技能时返回所有职位。
        raise ValueError("You should choose at least one skill.")
    if len(raw_skill_ids) > MAX_SELECTED_SKILLS:
        raise ValueError("Too many selected skills.")
    skill_ids = sorted({_positive_id(value, "skill ID") for value in raw_skill_ids})
    workplace_types = _choices(
        user_preferences.get("workplace_types"), WORKPLACE_TYPES, "workplace type"
    )
    employment_types = _choices(
        user_preferences.get("employment_types"), EMPLOYMENT_TYPE_MATCHES, "employment type"
    )
    education_level = user_preferences.get("education_level", "")
    if education_level is None:
        education_level = ""
    if not isinstance(education_level, str):
        raise ValueError("Invalid education level.")
    education_level = education_level.strip().lower()
    if education_level and education_level not in EDUCATION_RANKS:
        raise ValueError("Invalid education level.")

    minimum_salary = user_preferences.get("minimum_salary")
    if minimum_salary is not None:
        if isinstance(minimum_salary, bool) or not isinstance(minimum_salary, (int, float, Decimal)):
            raise ValueError("Minimum salary must be a finite, non-negative number.")
        minimum_salary = Decimal(str(minimum_salary))
        if not minimum_salary.is_finite() or not 0 <= minimum_salary <= Decimal("1e15"):
            raise ValueError("Minimum salary must be a finite, non-negative number no greater than 1e15.")
    salary_currency = user_preferences.get("salary_currency", "")
    if salary_currency is None:
        salary_currency = ""
    if not isinstance(salary_currency, str):
        raise ValueError("Invalid salary currency.")
    salary_currency = salary_currency.strip().upper()
    if salary_currency and not re.fullmatch(r"[A-Z]{3}", salary_currency):
        raise ValueError("Invalid salary currency.")
    if minimum_salary is not None and not salary_currency:
        raise ValueError("A salary currency is required for a minimum salary.")
    if salary_currency and minimum_salary is None:
        raise ValueError("A minimum salary is required when a currency is selected.")

    location_id = user_preferences.get("location_id")
    location_type = user_preferences.get("location_type", "")
    if location_type is None:
        location_type = ""
    if not isinstance(location_type, str):
        raise ValueError("Invalid location type.")
    location_country_id = user_preferences.get("location_country_id")
    if location_id is None:
        if location_type or location_country_id is not None:
            raise ValueError("Location ID, type and country must be supplied together.")
    else:
        location_id = _positive_id(location_id, "location ID")
        location_country_id = _country_group(_positive_id(location_country_id, "location country ID"))
        if location_type not in {"country", "province", "city"}:
            raise ValueError("Invalid location type.")
    connection = None
    cursor = None

    try:
        connection = get_database_connection()
        # 排名、详情和技能来自同一快照，避免并发更新造成缺项或前后不一致。
        connection.start_transaction(
            isolation_level="REPEATABLE READ", consistent_snapshot=True, readonly=True
        )
        cursor = connection.cursor(dictionary=True)

        skill_placeholders = ", ".join(["%s"] * len(skill_ids))
        cursor.execute(f"SELECT skill_id FROM skills WHERE skill_id IN ({skill_placeholders})", skill_ids)
        if {row["skill_id"] for row in cursor.fetchall()} != set(skill_ids):
            raise ValueError("Unknown skill ID.")

        selected_province_id = None
        if location_id is not None:
            cursor.execute(
                "SELECT geoname_id, location_type, country_id, province_id "
                "FROM locations WHERE geoname_id IN (%s, %s)",
                (location_id, location_country_id),
            )
            selected_rows = {row["geoname_id"]: row for row in cursor.fetchall()}
            country_row = selected_rows.get(location_country_id)
            if not country_row or country_row["location_type"] != "country":
                raise ValueError("Unknown location country ID.")
            selected_row = selected_rows.get(location_id)
            if selected_row:
                if _country_group(selected_row["country_id"]) != location_country_id:
                    raise ValueError("Location and country ID do not match.")
                region_as_province = location_id in CHINA_GROUP_IDS - {CHINA_COUNTRY_ID} and location_type == "province"
                if selected_row["location_type"] != location_type and not region_as_province:
                    raise ValueError("Location ID and type do not match.")
                selected_province_id = selected_row["province_id"]
            # 地图可能给出本地未收录的城市：仍按国家匹配，不猜省份、不发网络请求。
            if location_type == "province":
                selected_province_id = location_id

        workplace_parameters = list(workplace_types)
        workplace_filter_clause = " OR ".join(
            "FIND_IN_SET(%s, REPLACE(LOWER(COALESCE(jobs.workplace_type, '')), ' ', '')) > 0"
            for _ in workplace_types
        ) or "TRUE"
        employment_values = sorted({
            value for option in employment_types for value in EMPLOYMENT_TYPE_MATCHES[option]
        })

        if employment_values:
            employment_placeholders = ", ".join(["%s"] * len(employment_values))
            employment_filter_clause = f"""
                AND COALESCE(jobs.employment_type, '') IN ({employment_placeholders})
            """
            employment_parameters = list(employment_values)
        else:
            employment_filter_clause = ""
            employment_parameters = []

        salary_filter_enabled = minimum_salary is not None and minimum_salary > 0
        if salary_filter_enabled:
            if not salary_currency:
                raise ValueError("A salary currency is required for a minimum salary.")

            exchange_rates = load_cached_exchange_rates()
            input_currency_rate = exchange_rates.get(salary_currency)
            if input_currency_rate is None:
                raise ValueError(
                    f"No cached ECB exchange rate is available for {salary_currency}."
                )

            minimum_salary_eur = minimum_salary / Decimal(str(input_currency_rate))
            rate_case_lines = ["WHEN 'EUR' THEN annual_salary_min"]
            salary_parameters = []
            for currency, rate in sorted(exchange_rates.items()):
                if currency == "EUR":
                    continue
                rate_case_lines.append(
                    "WHEN %s THEN annual_salary_min / %s"
                )
                salary_parameters.extend([currency, Decimal(str(rate))])

            salary_candidates_cte = f"""
                salary_candidates AS (
                    SELECT *
                    FROM workplace_candidates
                    WHERE annual_salary_min > 0
                      AND CASE salary_currency
                          {' '.join(rate_case_lines)}
                          ELSE NULL
                      END >= %s
                )
            """
            salary_parameters.append(minimum_salary_eur)
        else:
            salary_candidates_cte = """
                salary_candidates AS (
                    SELECT *
                    FROM workplace_candidates
                )
            """
            salary_parameters = []
    
        placeholders = ", ".join(["%s"] * len(skill_ids))
        matching_skills_cte = f"""
            matching_skills AS (
                SELECT
                    job_skills.job_id,
                    SUM(CASE WHEN job_skills.skill_type = 'required' THEN 1 ELSE 0 END)
                        AS matched_required_count,
                    SUM(CASE WHEN job_skills.skill_type = 'preferred' THEN 1 ELSE 0 END)
                        AS matched_preferred_count
                FROM job_skills
                INNER JOIN salary_candidates
                    ON salary_candidates.job_id = job_skills.job_id
                WHERE job_skills.skill_id IN ({placeholders})
                GROUP BY job_skills.job_id
            )
        """
        skill_score_expression = """
            CASE
                WHEN job_skill_totals.required_count = 0
                     AND job_skill_totals.preferred_count = 0
                THEN 5
                WHEN job_skill_totals.preferred_count = 0
                THEN ROUND(
                    COALESCE(matching_skills.matched_required_count, 0)
                    / job_skill_totals.required_count * 100,
                    2
                )
                WHEN job_skill_totals.required_count = 0
                THEN ROUND(
                    COALESCE(matching_skills.matched_preferred_count, 0)
                    / job_skill_totals.preferred_count * 65,
                    2
                )
                WHEN COALESCE(matching_skills.matched_required_count, 0) = 0
                THEN ROUND(
                    COALESCE(matching_skills.matched_preferred_count, 0)
                    / job_skill_totals.preferred_count * 30,
                    2
                )
                ELSE ROUND(
                    matching_skills.matched_required_count
                    / job_skill_totals.required_count * 70
                    + COALESCE(matching_skills.matched_preferred_count, 0)
                    / job_skill_totals.preferred_count * 30,
                    2
                )
            END
        """
        skill_parameters = list(skill_ids)

        if workplace_types == ["remote"]:
            # 用户明确只选 Remote：按既定规则忽略所选地点，地点分为 10。
            location_ctes = """
                location_scores AS (
                    SELECT job_id, 10 AS location_score, 1 AS location_eligible
                    FROM salary_candidates
                )
            """
            location_parameters = []
        elif location_id is None:
            location_ctes = """
                location_scores AS (
                    SELECT job_id, 100 AS location_score, 1 AS location_eligible
                    FROM salary_candidates
                )
            """
            location_parameters = []
        else:
            # 仅当所选工作方式允许 Remote，才可走远程的跨国家例外。
            remote_option_allowed = not workplace_types or "remote" in workplace_types
            group_ids_sql = ", ".join(str(value) for value in sorted(CHINA_GROUP_IDS))
            job_country_expression = f"""
                CASE WHEN job_location.country_id IN ({group_ids_sql})
                     THEN {CHINA_COUNTRY_ID}
                     ELSE job_location.country_id END
            """
            location_ctes = f"""
                selected_location AS (
                    SELECT %s AS geoname_id, %s AS location_type,
                           %s AS country_id, %s AS province_id
                ),
                location_scores AS (
                    SELECT salary_candidates.job_id,
                        MAX(CASE
                            WHEN salary_candidates.offers_remote
                                 AND NOT salary_candidates.offers_nonremote THEN 10
                            WHEN {job_country_expression} IS NULL
                                 OR {job_country_expression} <> selected_location.country_id THEN 10
                            WHEN job_location.geoname_id = selected_location.geoname_id THEN 100
                            WHEN selected_location.location_type = 'province'
                                 AND job_location.location_type = 'city'
                                 AND job_location.province_id = selected_location.geoname_id THEN 80
                            WHEN selected_location.location_type = 'country'
                                 AND {job_country_expression} = selected_location.country_id THEN 80
                            WHEN selected_location.location_type = 'city'
                                 AND job_location.location_type = 'city'
                                 AND job_location.province_id = selected_location.province_id THEN 70
                            WHEN selected_location.location_type = 'city'
                                 AND job_location.location_type = 'province'
                                 AND job_location.geoname_id = selected_location.province_id THEN 50
                            WHEN selected_location.location_type = 'province'
                                 AND job_location.location_type = 'country'
                                 AND job_location.geoname_id = selected_location.country_id THEN 50
                            WHEN {job_country_expression} = selected_location.country_id THEN 30
                            ELSE 10
                        END) AS location_score,
                        MAX(CASE
                            WHEN %s = 1 AND salary_candidates.offers_remote THEN 1
                            WHEN {job_country_expression} = selected_location.country_id THEN 1
                            ELSE 0
                        END) AS location_eligible
                    FROM salary_candidates
                    CROSS JOIN selected_location
                    LEFT JOIN job_locations
                        ON job_locations.job_id = salary_candidates.job_id
                    LEFT JOIN locations AS job_location
                        ON job_location.geoname_id = job_locations.geoname_id
                    GROUP BY salary_candidates.job_id
                )
            """
            location_parameters = [
                location_id, location_type, location_country_id,
                selected_province_id, int(remote_option_allowed),
            ]

        query = f"""
            WITH workplace_candidates AS (
                SELECT
                    jobs.job_id,
                    jobs.workplace_type,
                    FIND_IN_SET('remote', REPLACE(LOWER(COALESCE(jobs.workplace_type, '')), ' ', '')) > 0
                        AS offers_remote,
                    (
                        FIND_IN_SET('hybrid', REPLACE(LOWER(COALESCE(jobs.workplace_type, '')), ' ', '')) > 0
                        OR FIND_IN_SET('onsite', REPLACE(LOWER(COALESCE(jobs.workplace_type, '')), ' ', '')) > 0
                    ) AS offers_nonremote,
                    UPPER(TRIM(COALESCE(jobs.salary_currency, ''))) AS salary_currency,
                    CASE jobs.salary_period
                        WHEN 'annual' THEN jobs.salary_min
                        WHEN 'monthly' THEN jobs.salary_min * 12
                        WHEN 'weekly' THEN jobs.salary_min * 52
                        WHEN 'biweekly' THEN jobs.salary_min * 26
                        WHEN 'daily' THEN jobs.salary_min
                            * COALESCE(jobs.working_days_per_week, 5) * 52
                        WHEN 'hourly' THEN jobs.salary_min
                            * COALESCE(jobs.working_hours_per_week, 40) * 52
                        ELSE NULL
                    END AS annual_salary_min
                FROM jobs
                WHERE
                    ({workplace_filter_clause})
                AND (
                    CASE jobs.minimum_education_level
                        WHEN 'high_school_or_below' THEN 0
                        WHEN 'bachelor' THEN 1
                        WHEN 'master' THEN 2
                        WHEN 'doctoral' THEN 3
                        ELSE -1
                    END <= %s
                )
                {employment_filter_clause}
            ),
            {salary_candidates_cte},
            job_skill_totals AS (
                SELECT
                    salary_candidates.job_id,
                    SUM(CASE WHEN job_skills.skill_type = 'required' THEN 1 ELSE 0 END)
                        AS required_count,
                    SUM(CASE WHEN job_skills.skill_type = 'preferred' THEN 1 ELSE 0 END)
                        AS preferred_count
                FROM salary_candidates
                LEFT JOIN job_skills
                    ON job_skills.job_id = salary_candidates.job_id
                GROUP BY salary_candidates.job_id
            ),
            {matching_skills_cte},
            skill_scores AS (
                SELECT
                    job_skill_totals.job_id,
                    {skill_score_expression} AS skill_score
                FROM job_skill_totals
                LEFT JOIN matching_skills
                    ON matching_skills.job_id = job_skill_totals.job_id
            ),
            {location_ctes},
            final_scores AS (
                SELECT
                    skill_scores.job_id,
                    skill_scores.skill_score,
                    location_scores.location_score,
                    location_scores.location_eligible,
                    ROUND(
                        skill_scores.skill_score * 0.40
                        + location_scores.location_score * 0.60,
                        2
                    ) AS score
                FROM skill_scores
                INNER JOIN location_scores
                    ON location_scores.job_id = skill_scores.job_id
            )
            SELECT
                job_id,
                skill_score,
                location_score,
                score,
                COUNT(*) OVER () AS total_matched_count
            FROM final_scores
            WHERE skill_score > 0
              AND location_eligible = 1
            ORDER BY score DESC, job_id ASC
            LIMIT 100
        """
    
        parameters = (
            workplace_parameters + [EDUCATION_RANKS.get(education_level, 3)]
            + employment_parameters
            + salary_parameters
            + skill_parameters
            + location_parameters
        )
        cursor.execute(query, parameters)
        ranked_rows = cursor.fetchall()

        total_matched_count = int(
            ranked_rows[0]["total_matched_count"]
            if ranked_rows
            else 0
        )

        for row in ranked_rows:
            row.pop("total_matched_count", None)

        ranked_by_job_id = {
            row["job_id"]: row
            for row in ranked_rows
        }
        ranked_job_ids = list(ranked_by_job_id)

        if not ranked_job_ids:
            return {
                "total_matched_count": 0,
                "displayed_count": 0,
                "display_limit": RESULT_DISPLAY_LIMIT,
                "jobs": [],
            }

        job_id_placeholders = ", ".join(["%s"] * len(ranked_job_ids))
        cursor.execute(f"""
            SELECT
                job_id,
                company,
                title,
                location,
                workplace_type,
                employment_type,
                experience_level,
                salary_min,
                salary_max,
                salary_currency,
                salary_period,
                working_hours_per_week,
                working_days_per_week,
                language_requirements,
                minimum_education_level,
                posted_date,
                application_deadline,
                application_url,
                role_summary
            FROM jobs
            WHERE job_id IN ({job_id_placeholders})
        """, ranked_job_ids)
        job_rows = cursor.fetchall()

        jobs_by_id = {}
        for job in job_rows:
            for field in (
                "salary_min",
                "salary_max",
                "working_hours_per_week",
                "working_days_per_week",
            ):
                if job[field] is not None:
                    job[field] = float(job[field])

            job["required_skills"] = []
            job["preferred_skills"] = []
            job.update(ranked_by_job_id[job["job_id"]])
            # 保留 SQL ROUND 的两位小数；旧 HTML 的 Overall Match Score 应接总分。
            job["skill_match_score"] = job["score"]
            jobs_by_id[job["job_id"]] = job

        if len(jobs_by_id) != len(ranked_job_ids):
            raise RuntimeError("Ranked job details are missing from the search snapshot.")

        cursor.execute(f"""
            SELECT
                job_skills.job_id,
                skills.skill_name,
                job_skills.skill_type
            FROM job_skills
            INNER JOIN skills
                ON skills.skill_id = job_skills.skill_id
            WHERE job_skills.job_id IN ({job_id_placeholders})
            ORDER BY job_skills.job_id, skills.skill_name
        """, ranked_job_ids)
        skill_rows = cursor.fetchall()

        for skill_row in skill_rows:
            job = jobs_by_id[skill_row["job_id"]]
            if skill_row["skill_type"] == "required":
                job["required_skills"].append(skill_row["skill_name"])
            elif skill_row["skill_type"] == "preferred":
                job["preferred_skills"].append(skill_row["skill_name"])

        jobs = [
            jobs_by_id[job_id]
            for job_id in ranked_job_ids
            if job_id in jobs_by_id
        ]

        return {
            "total_matched_count": total_matched_count,
            "displayed_count": len(jobs),
            "display_limit": RESULT_DISPLAY_LIMIT,
            "jobs": jobs,
        }
    except mysql.connector.Error:
        logger.exception("Database search failed.")
        raise

    finally:
        # 某个 close 失败也继续释放另一个资源，避免掩盖原始搜索异常。
        for resource in (cursor, connection):
            if resource is not None:
                try:
                    resource.close()
                except mysql.connector.Error:
                    logger.warning("Could not close a search database resource.", exc_info=True)
