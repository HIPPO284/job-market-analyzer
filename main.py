print("hello hippo")
print("Job Market Analyzer")

from jobs_data import jobs

#user_preferences = {
#    "locations": ["Edmonton", "Calgary", "Canada Remote"],
#    "minimum_salary": 60000,
#    "skills": {"python", "java", "git"},
#    "experience_levels": ["internship", "entry"],
#    "workplace_types": ["remote", "hybrid"],
#    "employment_types": ["internship", "full_time", "part_time"],
#}
def clean_text_list(text):
    cleaned_items = []
    for item in text.split(","):
        clean_item = item.strip().lower()
        if clean_item:
            cleaned_items.append(clean_item)
    return cleaned_items

def get_valid_minimum_salary():
    while True:
        salary_text = input("Enter minimum salary: ")
        try:
            cleaned_salary_text = salary_text.strip().replace(",", "").replace(".", "")
            cleaned_salary_text = cleaned_salary_text.replace(" ", "")
            minimum_salary = int(cleaned_salary_text)
            if minimum_salary < 0:
                print("Salary cannot be negative. Please try again.")
                continue
            return minimum_salary
        except ValueError:
            print("Please enter a whole number, for example: 60000.")

def get_user_preferences():
    locations_text = input("Enter locations, separated by commas: ")
    skills_text = input("Enter skills: ")
    experience_levels_text = input("Enter experience levels: ")
    workplace_types_text = input("Enter workplace types: ")
    employment_types_text = input("Enter employment types: ")
    locations = clean_text_list(locations_text)
    minimum_salary = get_valid_minimum_salary()
    skills = set(clean_text_list(skills_text))
    experience_levels = clean_text_list(experience_levels_text)
    workplace_types = clean_text_list(workplace_types_text)
    employment_types = clean_text_list(employment_types_text)
    user_preferences = {
        "locations": locations,
        "minimum_salary": minimum_salary,
        "skills": skills,
        "experience_levels": experience_levels,
        "workplace_types": workplace_types,
        "employment_types": employment_types,
    }
    return user_preferences

user_preferences = get_user_preferences()


#print(len(jobs))
#print(jobs[0]["title"])

def filter_by_workplace_types(jobs, workplace_types):
    workplace_selected_jobs = []
    for job in jobs:
        if job["workplace_type"] in workplace_types:
            workplace_selected_jobs.append(job)
    return workplace_selected_jobs

def filter_by_employment_types(jobs, employment_types):
    employment_selected_jobs = []
    for job in jobs:
        if job["employment_type"] in employment_types:
            employment_selected_jobs.append(job)
    return employment_selected_jobs

def filter_by_experience_levels(jobs, experience_levels):
    experience_selected_jobs = []
    for job in jobs:
        if job["experience_level"] in experience_levels:
            experience_selected_jobs.append(job)
    return experience_selected_jobs

def print_job(job):
    for key,value in job.items():
        print(f"{key}: {value}")

#print_job(jobs[0])

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

#print(len(edmonton_jobs))
#print(edmonton_jobs[0]["title"])


def filter_by_min_salary(jobs, minimum_salary):
    salary_selected_list = []
    for job in jobs:
        if minimum_salary <= job["salary_min"]:
            salary_selected_list.append(job)
    return salary_selected_list
min_salary_jobs = filter_by_min_salary(jobs, minimum_salary=65000)

#print(len(min_salary_jobs))
#print(min_salary_jobs[0]["title"])

def location_min_salary_combine(jobs, locations, minimum_salary):
    min_salary_jobs = filter_by_min_salary(jobs, minimum_salary)
    location_salary_jobs = filter_by_multiple_locations(
        min_salary_jobs,
        locations
    )

    return location_salary_jobs

#print(user_preferences["locations"][0])
#print(user_preferences["minimum_salary"])
#print("python" in user_preferences["skills"])


#location_salary_jobs = location_min_salary_combine(
#    jobs,
#    user_preferences["locations"],
#    user_preferences["minimum_salary"]
#)

#print(len(location_salary_jobs))

#for job in location_salary_jobs:
#    print(job["id"], job["title"])

def matched_required_skills(job, user_skills):
    required_skills = set(job["required_skills"])
    skill_selected_set = required_skills & user_skills

    return skill_selected_set


job_1_matched_skills = matched_required_skills(
    jobs[0],
    user_preferences["skills"]
)

#print(len(job_1_matched_skills))
#print("python" in job_1_matched_skills)
#print("git" in job_1_matched_skills)
#print("sql" in job_1_matched_skills)
#print(job_1_matched_skills)

def missing_required_skills(job, user_skills):
    required_skills = set(job["required_skills"])
    skill_missing_set = required_skills - user_skills

    return skill_missing_set
#print(missing_required_skills(jobs[0], user_preferences["skills"]))

#print(missing_required_skills(jobs[4], user_preferences["skills"]))
#print(missing_required_skills(jobs[9], user_preferences["skills"]))

def calculate_skill_match_score(job, user_skills):
    required_skills = set(job["required_skills"])
    if not required_skills:
        return 0.0
    matched_skills = matched_required_skills(job, user_skills)
    score = round(len(matched_skills) / len(required_skills) * 100,2)
    return score

#print(f"{calculate_skill_match_score(jobs[0], user_preferences["skills"])} %")


#def build_job_recommendation(job, user_skills):
#    skills_combination = {}
#    skills_combination["job_id"] = job["id"]
#    skills_combination["title"] = job["title"]
#    skills_combination["skill_match_score"] = calculate_skill_match_score(job, user_skills)
#    skills_combination["matched_skills"] = matched_required_skills(job, user_skills)
#    skills_combination["missing_skills"] = missing_required_skills(job, user_skills)
#    return skills_combination

#job_1_recommendation = build_job_recommendation(jobs[0],user_preferences["skills"])
#print(job_1_recommendation)

def build_job_recommendation(job, user_skills):
    recommendation = {}
    recommendation["job_id"] = job["id"]
    recommendation["title"] = job["title"]
    recommendation["company"] = job["company"]
    recommendation["location"] = job["location"]
    recommendation["workplace_type"] = job["workplace_type"]
    recommendation["employment_type"] = job["employment_type"]
    recommendation["salary_min"] = job["salary_min"]
    recommendation["salary_max"] = job["salary_max"]
    recommendation["skill_match_score"] = calculate_skill_match_score(job,user_skills)
    recommendation["matched_skills"] = matched_required_skills(job,user_skills)
    recommendation["missing_skills"] = missing_required_skills(job,user_skills)
    recommendation["preferred_skills"] = job["preferred_skills"]
    return recommendation



def generate_recommendations(jobs, user_preferences):
    recommendations = []
    overall_selected_jobs = location_min_salary_combine(jobs, user_preferences["locations"], user_preferences["minimum_salary"])
    overall_selected_jobs = filter_by_workplace_types(overall_selected_jobs, user_preferences["workplace_types"])
    overall_selected_jobs = filter_by_employment_types(overall_selected_jobs, user_preferences["employment_types"])
    overall_selected_jobs = filter_by_experience_levels(overall_selected_jobs, user_preferences["experience_levels"])
    for job in overall_selected_jobs:
        r = build_job_recommendation(job,user_preferences["skills"])
        recommendations.append(r)
    return recommendations

def get_match_score(recommendation):
    return recommendation["skill_match_score"]


def sort_recommendations(recommendations):
    return sorted(recommendations,key=get_match_score,reverse=True)

#recommendations = generate_recommendations(jobs,user_preferences)

#sorted_recommendations = sort_recommendations(recommendations)

#for recommendation in sorted_recommendations:
#    print(recommendation["job_id"],recommendation["title"],recommendation["skill_match_score"])

recommendations = generate_recommendations(jobs, user_preferences)
sorted_recommendations = sort_recommendations(recommendations)

#print_recommendations(sorted_recommendations)

def print_recommendation(recommendation):
    print("-" * 50)

    basic_fields = [
        ("Job ID", "job_id"),
        ("Title", "title"),
        ("Company", "company"),
        ("Location", "location"),
        ("Workplace Type", "workplace_type"),
        ("Employment Type", "employment_type"),
    ]

    for label, key in basic_fields:
        print(f"{label}: {recommendation[key]}")

    print(f"Salary Range: ${recommendation['salary_min']:,} - ${recommendation['salary_max']:,}")
    print(f"Skill Match Score: {recommendation['skill_match_score']}%")
    print(f"Matched Required Skills: {format_skills(recommendation['matched_skills'])}")
    print(f"Missing Required Skills: {format_skills(recommendation['missing_skills'])}")
    print(f"Preferred Skills: {format_skills(recommendation['preferred_skills'])}")
    print("-" * 50)


def format_skills(skills):
    if not skills:
        return "None"
    sorted_skills = sorted(skills)
    skills_text = ", ".join(sorted_skills)
    return skills_text



def print_recommendations(recommendations):
    if not recommendations:        # recommendations为空列表
        print("No matching jobs found.")
        print("Try changing your location, salary, workplace type, or employment type.")
        return
    for recommendation in recommendations:
        print_recommendation(recommendation)

print_recommendations(sorted_recommendations)










