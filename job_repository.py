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
            application_url
        FROM jobs
        ORDER BY job_id;
    """)

    jobs = cursor.fetchall()

    for job in jobs:
        job["required_skills"] = []
        job["preferred_skills"] = []

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

    cursor.close()
    connection.close()

    return jobs