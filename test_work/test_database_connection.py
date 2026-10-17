from job_repository import get_all_jobs


jobs = get_all_jobs()

print(f"Jobs loaded from MySQL: {len(jobs)}")
print(jobs[0])
print(jobs[0]["title"])
print(jobs[0]["required_skills"])
print(jobs[0]["preferred_skills"])
print(jobs[0]["salary_min"])
print(jobs[0]["salary_max"])
print(jobs[0]["working_hours_per_week"])
print(jobs[0]["working_days_per_week"])
print(jobs[0]["salary_period"])
print(jobs[0]["salary_currency"])
