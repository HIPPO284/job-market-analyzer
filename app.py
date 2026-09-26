from flask import Flask, render_template, request
from recommendation_service import clean_text_list, recommend_jobs
app = Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hippo", methods=["POST"])
def hippo():
    skills = request.form["skills"]
    locations = request.form["locations"]
    workplace_type = request.form["workplace_type"]
    experience_level = request.form["experience_level"]
    employment_type = request.form["employment_type"]
    education_level = request.form["education_level"]
    salary_currency = request.form.get("salary_currency", "")

    minimum_salary_text = request.form.get("minimum_salary", "").strip()

    if not minimum_salary_text:
        minimum_salary = None
    else:
        try:
            minimum_salary = int(minimum_salary_text)
        except ValueError:
            return "Please enter a whole number for minimum salary."

        if minimum_salary < 0:
            return "Minimum salary cannot be negative."
    if minimum_salary is not None and not salary_currency:
        return "Please select a currency when you enter a minimum salary."

    if salary_currency and minimum_salary is None:
        return "Please enter a minimum salary when you select a currency."
    skills = set(clean_text_list(skills))
    locations = clean_text_list(locations)
    user_preferences = {
        "locations": locations,
        "minimum_salary": minimum_salary,
        "skills": skills,
        "experience_levels": [experience_level],
        "workplace_types": [workplace_type],
        "employment_types": [employment_type],
        "education_level": education_level,
        "salary_currency": salary_currency,
    }
    recommendations = recommend_jobs(user_preferences)
    return render_template(
        "results.html",
        recommendations=recommendations,
        user_preferences=user_preferences
    )

# return f"Skills: {skills}; Locations: {locations}; Minimum Salary: {minimum_salary}; Workplace Type: {workplace_type}; Experience Level: {experience_level}; Employment Type: {employment_type}"


if __name__ == "__main__":
    app.run(debug=True)