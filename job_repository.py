from database import get_database_connection


def get_all_jobs():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            job_id AS id,
            company,
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
            salary_currency,
            salary_period,
            working_hours_per_week,
            working_days_per_week,
            role_summary
        FROM jobs
        ORDER BY job_id;
    """)

    jobs = cursor.fetchall()        # all job from database

    for job in jobs:
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
        job["locations"] = []

    jobs_by_id = {}

    for job in jobs:
        jobs_by_id[job["id"]] = job

    cursor.execute("""
        SELECT
            job_skills.job_id,
            skills.skill_name,
            job_skills.skill_type
        FROM job_skills
        INNER JOIN skills
            ON skills.skill_id = job_skills.skill_id
        ORDER BY job_skills.job_id, skills.skill_name;
    """)

    skill_rows = cursor.fetchall()

    for skill_row in skill_rows:
        job = jobs_by_id[skill_row["job_id"]]

        if skill_row["skill_type"] == "required":
            job["required_skills"].append(skill_row["skill_name"])
        else:
            job["preferred_skills"].append(skill_row["skill_name"])
    cursor.execute("""
                   SELECT job_locations.job_id,
                          locations.geoname_id,
                          locations.location_type,
                          locations.country_id,
                          locations.province_id
                   FROM job_locations
                            INNER JOIN locations
                                       ON locations.geoname_id = job_locations.geoname_id
                   ORDER BY job_locations.job_id, locations.geoname_id;
                   """)

    location_rows = cursor.fetchall()

    for location_row in location_rows:
        job = jobs_by_id[location_row["job_id"]]

        job["locations"].append({
            "geoname_id": location_row["geoname_id"],
            "location_type": location_row["location_type"],
            "country_id": location_row["country_id"],
            "province_id": location_row["province_id"],
        })

    cursor.close()
    connection.close()

    return jobs


