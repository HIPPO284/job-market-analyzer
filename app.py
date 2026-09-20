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
    try:
        minimum_salary = int(request.form["minimum_salary"])
    except ValueError:
        return "Please enter a whole number for minimum salary."

    if minimum_salary < 0:
        return "Minimum salary cannot be negative."
    skills = set(clean_text_list(skills))
    locations = clean_text_list(locations)
    user_preferences = {
        "locations": locations,
        "minimum_salary": minimum_salary,
        "skills": skills,
        "experience_levels": [experience_level],
        "workplace_types": [workplace_type],
        "employment_types": [employment_type]
    }
    recommendations = recommend_jobs(user_preferences)
    return render_template(
        "results.html",
        recommendations=recommendations,
        user_preferences=user_preferences
    )

    return f"Skills: {skills}; Locations: {locations}; Minimum Salary: {minimum_salary}; Workplace Type: {workplace_type}; Experience Level: {experience_level}; Employment Type: {employment_type}"


if __name__ == "__main__":
    app.run(debug=True)