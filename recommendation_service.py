from job_repository import get_all_jobs
from datetime import date, datetime
import currencies
import math


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

    selected_jobs = []

    for job in jobs:
        job_workplace_types = job["workplace_type"]

        if job_workplace_types is None:
            job_workplace_types = []
        elif isinstance(job_workplace_types, str):
            job_workplace_types = clean_text_list(job_workplace_types)

        for workplace_type in job_workplace_types:
            if workplace_type in workplace_types:
                selected_jobs.append(job)
                break

    return selected_jobs

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

def filter_by_country(jobs, location_country_id):
    if location_country_id is None:
        return jobs

    selected_jobs = []
    for job in jobs:
        for location in job["locations"]:
            if location["country_id"] == location_country_id:
                selected_jobs.append(job)
                break

    return selected_jobs

def filter_by_min_salary(jobs, minimum_salary, currency):
    # A zero value means the user did not set a real salary threshold.
    if minimum_salary is None or minimum_salary <= 0:
        return jobs
    if currency is None:
        return jobs
    exchange_rates = currencies.fetch_exchange_rates()
    salary_selected_list = []
    for job in jobs:
        corp_annul_salary = currencies.calculate_annual_salary(job["salary_min"], job["salary_period"], job["working_hours_per_week"],job["working_days_per_week"])
        job_amount = currencies.convert_to_eur(corp_annul_salary, job["salary_currency"], exchange_rates)
        output_amount = currencies.convert_to_input_currency(job_amount, currency, exchange_rates)
        if output_amount is not None and (output_amount >= minimum_salary or math.isclose(output_amount, minimum_salary, rel_tol=0, abs_tol=1e-8)):
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

def location_min_salary_combine(jobs, location_country_id, minimum_salary, currency):
    min_salary_jobs = filter_by_min_salary(jobs, minimum_salary, currency)
    return filter_by_country(min_salary_jobs, location_country_id)

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

def filter_by_application_deadline(jobs):
    today = date.today()
    ddl_selected_list = []
    for job in jobs:
        ddl = job["application_deadline"]
        if not ddl or ddl > today:
            ddl_selected_list.append(job)
    return ddl_selected_list





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

def salary_normalizer(job, user_preferences):
    period_units = {
        "hourly": "hour",
        "daily": "day",
        "annual": "year",
        "monthly": "month",
        "weekly": "week",
        "biweekly": "2 weeks",
    }
    salary_min = job["salary_min"]
    salary_max = job["salary_max"]
    salary_currency = job["salary_currency"]
    currency_text = salary_currency or "(currency not specified)"
    salary_period = job["salary_period"]
    preferred_salary = user_preferences["minimum_salary"]
    input_currency = user_preferences["salary_currency"]
    exchange_rates = currencies.fetch_exchange_rates()

    if salary_period in period_units:
        period_text = f"/{period_units[salary_period]}"
    else:
        period_text = " (pay period not specified)"

    if salary_min is None:
        min_text = "Minimum salary not available"
    else:
        min_text = f"{salary_min} {currency_text}{period_text}"

    if salary_max is None:
        max_text = "Maximum salary not available"
    else:
        max_text = f"{salary_max} {currency_text}{period_text}"


    if preferred_salary is None:
        pass

    elif not input_currency or input_currency == salary_currency:
        pass

    elif not salary_currency or exchange_rates is None:
        pass

    else:
        if salary_min is not None:
            inter = currencies.convert_to_eur(salary_min, salary_currency, exchange_rates)
            min_salary = currencies.convert_to_input_currency(inter, input_currency, exchange_rates)
            if min_salary is not None:
                min_text = f"{min_text} \u2248 {min_salary:.2f} {input_currency}{period_text}"

        if salary_max is not None:
            inter = currencies.convert_to_eur(salary_max, salary_currency, exchange_rates)
            max_salary = currencies.convert_to_input_currency(inter, input_currency, exchange_rates)
            if max_salary is not None:
                max_text = f"{max_text} \u2248 {max_salary:.2f} {input_currency}{period_text}"

    return min_text, max_text

def build_job_recommendation(job, user_skills, user_preferences):
    salary_min, salary_max = salary_normalizer(job, user_preferences)
    recommendation = {}
    recommendation["job_id"] = job["id"]
    recommendation["title"] = job["title"]
    recommendation["company"] = job["company"]
    recommendation["role_summary"] = job.get("role_summary")
    recommendation["location"] = job["location"]
    recommendation["workplace_type"] = job["workplace_type"]
    recommendation["employment_type"] = job["employment_type"]
    recommendation["salary_min"] = salary_min
    recommendation["salary_max"] = salary_max
    recommendation["salary_currency"] = job["salary_currency"]
    recommendation["salary_period"] = job["salary_period"]
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
    location_country_id = user_preferences["location_country_id"]

    if user_preferences["workplace_types"] == ["remote"]:
        location_country_id = None

    overall_selected_jobs = location_min_salary_combine(jobs,location_country_id,user_preferences["minimum_salary"],user_preferences["salary_currency"],)
    overall_selected_jobs = filter_by_workplace_types(overall_selected_jobs,user_preferences["workplace_types"],)
    overall_selected_jobs = filter_by_employment_types(overall_selected_jobs, user_preferences["employment_types"])
    overall_selected_jobs = filter_by_experience_levels(overall_selected_jobs, user_preferences["experience_levels"])
    overall_selected_jobs = filter_by_education_level(overall_selected_jobs,user_preferences["education_level"])
    overall_selected_jobs = filter_by_application_deadline(overall_selected_jobs)

    for job in overall_selected_jobs:
        required_matches = matched_required_skills(
            job, user_preferences["skills"]
        )
        preferred_matches = matched_preferred_skills(
            job, user_preferences["skills"]
        )
        if user_preferences["skills"] and not required_matches and not preferred_matches:
            continue

        r = build_job_recommendation(job, user_preferences["skills"], user_preferences)
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
















