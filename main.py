print("hello hippo")
print("Job Market Analyzer")

from jobs_data import jobs
print(len(jobs))
print(jobs[0]["title"])

def print_job(job):
    for key,value in job.items():
        print(f"{key}: {value}")


print_job(jobs[0])


def filter_by_location(jobs, location):
    location_selected_list = []
    for job in jobs:
        if location.lower() in job["location"].lower():
            location_selected_list.append(job)
    return location_selected_list

edmonton_jobs = filter_by_location(jobs, location="Edmonton")

print(len(edmonton_jobs))
print(edmonton_jobs[0]["title"])









