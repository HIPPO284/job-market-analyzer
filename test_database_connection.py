from job_repository import get_all_jobs


jobs = get_all_jobs()

print(f"Jobs loaded from MySQL: {len(jobs)}")
print(jobs[0])
print(jobs[0]["title"])
print(jobs[0]["required_skills"])
print(jobs[0]["preferred_skills"])