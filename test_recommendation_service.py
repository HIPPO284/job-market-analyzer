from recommendation_service import recommend_jobs
user_preferences = {
    "locations": ["Edmonton", "Calgary", "Canada Remote"],
    "location_country_id": 6251999,
    "minimum_salary": 6000,
    "salary_currency": "CAD",
    "skills": {"python", "java", "git"},
    "experience_levels": ["entry"],
    "workplace_types": ["hybrid"],
    "employment_types": ["internship", "full_time"],
    "education_level": "bachelor",
}

recommendations = recommend_jobs(user_preferences)

print(f"Recommendations found: {len(recommendations)}")

for recommendation in recommendations:
    print(
        recommendation["title"],
        recommendation["skill_match_score"]

    )