print("hello hippo")
print("Job Market Analyzer")

from jobs_data import jobs

user_preferences = {
    "locations": ["Edmonton", "Calgary", "Canada Remote"],
    "minimum_salary": 60000,
    "skills": {"python", "java", "git"},
    "preferred_roles": [
        "software developer",
        "data analyst",
        "qa automation"
    ],
    "workplace_types": ["remote", "hybrid"],
    "employment_types": ["internship", "full_time", "part_time"],
}

print(len(jobs))
print(jobs[0]["title"])

def print_job(job):
    for key,value in job.items():
        print(f"{key}: {value}")


print_job(jobs[0])

def filter_by_multiple_locations(jobs, locations):
    location_selected_list = []

    for job in jobs:
        for location in locations:
            if location.lower() in job["location"].lower():
                location_selected_list.append(job)
                break

    return location_selected_list

def filter_by_location(jobs, location):
    location_selected_list = []
    for job in jobs:
        if location.lower() in job["location"].lower():
            location_selected_list.append(job)
    return location_selected_list

edmonton_jobs = filter_by_location(jobs, location="Edmonton")

print(len(edmonton_jobs))
print(edmonton_jobs[0]["title"])


def filter_by_min_salary(jobs, minimum_salary):
    salary_selected_list = []
    for job in jobs:
        if minimum_salary <= job["salary_min"]:
            salary_selected_list.append(job)
    return salary_selected_list
min_salary_jobs = filter_by_min_salary(jobs, minimum_salary=65000)

print(len(min_salary_jobs))
print(min_salary_jobs[0]["title"])

def location_min_salary_combine(jobs, locations, minimum_salary):
    min_salary_jobs = filter_by_min_salary(jobs, minimum_salary)
    location_salary_jobs = filter_by_multiple_locations(
        min_salary_jobs,
        locations
    )

    return location_salary_jobs

print(user_preferences["locations"][0])
print(user_preferences["minimum_salary"])
print("python" in user_preferences["skills"])




location_salary_jobs = location_min_salary_combine(
    jobs,
    user_preferences["locations"],
    user_preferences["minimum_salary"]
)

print(len(location_salary_jobs))

for job in location_salary_jobs:
    print(job["id"], job["title"])











