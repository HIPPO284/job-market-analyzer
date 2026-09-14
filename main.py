print("hello hippo")
print("Job Market Analyzer")

from jobs_data import jobs
print(len(jobs))
print(jobs[0]["title"])

def print_job(job):
    for key,value in job.items():
        print(f"{key}: {value}")


print_job(jobs[0])