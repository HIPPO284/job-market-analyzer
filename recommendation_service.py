from job_repository import get_all_jobs

EDUCATION_RANKS = {
    "high_school_or_below": 0,
    "bachelor": 1,
    "master": 2,
    "doctoral": 3,
}

def clean_text_list(text):
    cleaned_items = []
    for item in text.split(","):
        clean_item = item.strip().lower()
        if clean_item:
            cleaned_items.append(clean_item)
    return cleaned_items

def filter_by_workplace_types(jobs, workplace_types):
    if not workplace_types or not any(workplace_types):
        return jobs
    workplace_selected_jobs = []
    for job in jobs:
        if job["workplace_type"] in workplace_types:
            workplace_selected_jobs.append(job)
    return workplace_selected_jobs

def filter_by_employment_types(jobs, employment_types):
    if not employment_types or not any(employment_types):
        return jobs
    employment_selected_jobs = []
    for job in jobs:
        if job["employment_type"] in employment_types:
            employment_selected_jobs.append(job)
    return employment_selected_jobs

def filter_by_experience_levels(jobs, experience_levels):
    if not experience_levels or not any(experience_levels):
        return jobs
    experience_selected_jobs = []
    for job in jobs:
        if job["experience_level"] in experience_levels:
            experience_selected_jobs.append(job)
    return experience_selected_jobs

def filter_by_multiple_locations(jobs, locations):
    if not locations:
        return jobs
    location_selected_list = []
    for job in jobs:
        for location in locations:
            if location.lower() in job["location"].lower():
                location_selected_list.append(job)
                break

    return location_selected_list

def filter_by_min_salary(jobs, minimum_salary):
    if minimum_salary is None:
        return jobs
    salary_selected_list = []
    for job in jobs:
        if minimum_salary <= job["salary_min"]:
            salary_selected_list.append(job)
    return salary_selected_list


def filter_by_education_level(jobs, education_level):
    if not education_level:
        return jobs
    education_level_selected_jobs = []
    for job in jobs:
        required_education_levels = job["minimum_education_level"]
        if not required_education_levels:
            education_level_selected_jobs.append(job)
        else:
            filter_rank = EDUCATION_RANKS[education_level]
            if filter_rank >= EDUCATION_RANKS[required_education_levels]:
                education_level_selected_jobs.append(job)
    return education_level_selected_jobs


    #print(len(min_salary_jobs))
#print(min_salary_jobs[0]["title"])

def location_min_salary_combine(jobs, locations, minimum_salary):
    min_salary_jobs = filter_by_min_salary(jobs, minimum_salary)
    location_salary_jobs = filter_by_multiple_locations(
        min_salary_jobs,
        locations
    )

    return location_salary_jobs

def matched_required_skills(job, user_skills):
    required_skills = set(job["required_skills"])
    skill_selected_set = required_skills & user_skills

    return skill_selected_set

def matched_preferred_skills(job, user_skills):
    preferred_skills = set(job["preferred_skills"])
    return preferred_skills & user_skills

def missing_required_skills(job, user_skills):
    required_skills = set(job["required_skills"])
    skill_missing_set = required_skills - user_skills

    return skill_missing_set

def calculate_skill_match_score(job, user_skills):
    required_skills = set(job["required_skills"])
    preferred_skills = set(job["preferred_skills"])
    matched_skills_required = matched_required_skills(job, user_skills)
    if not required_skills or not matched_skills_required:
        return 0.0
    elif not preferred_skills:
        matched_skills_required = matched_required_skills(job, user_skills)
        score = round(len(matched_skills_required) / len(required_skills) * 100,2)
    else:
        matched_skills_required = matched_required_skills(job, user_skills)
        matched_skills_preferred = matched_preferred_skills(job, user_skills)
        score = round((len(matched_skills_required) / len(required_skills) * 70) + (len(matched_skills_preferred) / len(preferred_skills) * 30),2)
    return score

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
    recommendation["skill_match_score"] = calculate_skill_match_score(job, user_skills)
    recommendation["matched_skills"] = matched_required_skills(job,user_skills)
    recommendation["missing_skills"] = missing_required_skills(job,user_skills)
    recommendation["preferred_skills"] = job["preferred_skills"]
    recommendation["experience_level"] = job["experience_level"]
    recommendation["required_skills"] = job["required_skills"]
    recommendation["minimum_education_level"] = job["minimum_education_level"]
    recommendation["posted_date"] = job["posted_date"]
    recommendation["application_deadline"] = job["application_deadline"]
    recommendation["application_url"] = job["application_url"]
    return recommendation



def generate_recommendations(jobs, user_preferences):
    recommendations = []
    overall_selected_jobs = location_min_salary_combine(jobs, user_preferences["locations"], user_preferences["minimum_salary"])
    overall_selected_jobs = filter_by_workplace_types(overall_selected_jobs, user_preferences["workplace_types"])
    overall_selected_jobs = filter_by_employment_types(overall_selected_jobs, user_preferences["employment_types"])
    overall_selected_jobs = filter_by_experience_levels(overall_selected_jobs, user_preferences["experience_levels"])
    overall_selected_jobs = filter_by_education_level(overall_selected_jobs,user_preferences["education_level"])
    for job in overall_selected_jobs:
        r = build_job_recommendation(job,user_preferences["skills"])
        recommendations.append(r)
    return recommendations

def get_match_score(recommendation):
    return recommendation["skill_match_score"]


def sort_recommendations(recommendations):
    return sorted(recommendations,key=get_match_score,reverse=True)


def recommend_jobs(user_preferences):
    jobs = get_all_jobs()
    recommendations = generate_recommendations(jobs, user_preferences)
    recommendations = sort_recommendations(recommendations)
    return recommendations
















