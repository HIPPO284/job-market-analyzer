from flask import Flask, render_template, request, jsonify, abort, send_from_directory
from skill_normalizer import all_skills, find_skill_suggestions, return_suggestions
from database import get_database_connection
import math
from search_repository import search_jobs, EDUCATION_RANKS
from routes import build_location_options
from analytics.search_event_logger import append_search_event
from analytics.analytics_reader import load_analytics_data
from pathlib import Path
from urllib.parse import urlsplit

app = Flask(__name__)    #Create Flask application object, the entire backend program.
@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/skills")
def api_skills():
    skill_text = request.args.get("q", "").strip()     # like a dictionary {"q" : value}

    if len(skill_text) == 0 or len(skill_text) > 100:
        return jsonify([])

    sorted_entries = find_skill_suggestions(skill_text,all_skills,)
    suggestions = return_suggestions(sorted_entries,all_skills,)
    return jsonify(suggestions)

@app.post("/api/location")
def api_location():
    location_options = []
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Please send a JSON object."}), 400
    if isinstance(data.get("latitude"), bool) or isinstance(data.get("longitude"), bool):
        return jsonify({"error": "Coordinates must be numbers."}), 400
    try:
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))
    except (TypeError, ValueError, OverflowError):
        return jsonify({"error": "Please provide valid coordinates."}), 400
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return jsonify({"error": "Coordinates are out of range."}), 400
    location_options = build_location_options(latitude, longitude)
    if location_options is None:
        return jsonify({"error": "Could not fetch location options"}), 502

    return jsonify(location_options)


@app.route("/hippo", methods=["POST"])
def hippo():
    raw_skill_ids = request.form.getlist("skill_ids")

    if len(raw_skill_ids) > 50:
        abort(400, description="Too many selected skills.")

    try:
        skill_ids = sorted({int(value) for value in raw_skill_ids})
    except ValueError:
        abort(400, description="Invalid skill ID.")

    if any(value <= 0 or value > 2**31 - 1 for value in skill_ids):
        abort(400, description="Invalid skill ID.")
    if not skill_ids:
        abort(400, description="Please choose at least one skill.")

    skills = set()

    if skill_ids:
        connection = get_database_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            placeholders = ", ".join(["%s"] * len(skill_ids))

            cursor.execute(
                f"""
                SELECT skill_id, skill_name
                FROM skills
                WHERE skill_id IN ({placeholders})
                """,
                tuple(skill_ids),
            )

            rows = cursor.fetchall()

            if len(rows) != len(skill_ids):
                abort(400, description="Unknown skill ID.")

            skills = {row["skill_name"] for row in rows}

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
    location_name = request.form.get("locations", "").strip()
    location_id = request.form.get("location_id", type=int)
    location_type = request.form.get("location_type", "").strip()
    location_country_id = request.form.get("location_country_id", type=int)
    if location_id is not None and location_country_id is None:
        abort(400, description="Missing or invalid location country ID.")
    if location_country_id is not None and location_country_id <= 0:
        abort(400, description="Invalid location country ID.")
    workplace_type = request.form["workplace_type"]
    employment_type = request.form["employment_type"]
    if employment_type not in {"", "internship", "full_time", "part_time"}:
        abort(400, description="Invalid employment type.")
    education_level = request.form["education_level"]

    if education_level and education_level not in EDUCATION_RANKS:
        abort(400, description="Invalid education level.")
    salary_currency = request.form.get("salary_currency", "")

    minimum_salary_text = request.form.get("minimum_salary", "").strip()

    if not minimum_salary_text:
        minimum_salary = None
    else:
        try:
            minimum_salary = float(minimum_salary_text)
        except ValueError:
            return "Please enter a valid number for minimum salary.", 400

        if not math.isfinite(minimum_salary) or minimum_salary < 0:
            return "Minimum salary must be a finite, non-negative number.", 400
    if minimum_salary is not None and not salary_currency:
        return "Please select a currency when you enter a minimum salary.", 400

    if salary_currency and minimum_salary is None:
        return "Please enter a minimum salary when you select a currency.", 400

    locations = [location_name] if location_name else []
    user_preferences = {
        "locations": locations,
        "minimum_salary": minimum_salary,
        "skills": skills,
        "skill_ids": skill_ids,
        "workplace_types": [workplace_type],
        "employment_types": [employment_type],
        "education_level": education_level,
        "salary_currency": salary_currency,
        "location_id": location_id,
        "location_type": location_type,
        "location_country_id": location_country_id,
    }
    search_result = search_jobs(user_preferences)
    try:
        append_search_event(user_preferences, search_result)
    except (OSError, TypeError, ValueError) as error:
        app.logger.warning("Could not save search analytics: %s", error) # %s,   把 error 的内容填到 %s 所在的位置
    recommendations = search_result["jobs"]
    for job in recommendations:        #   check if a real URL
        try:
            parsed_url = urlsplit(job["application_url"] or "")
            if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname:
                job["application_url"] = None
        except ValueError:
            job["application_url"] = None
    return render_template(
        "results.html",
        recommendations=recommendations,
        total_matched_count=search_result["total_matched_count"],
        displayed_count=search_result["displayed_count"],
        display_limit=search_result["display_limit"],
    )

# return f"Skills: {skills}; Locations: {locations}; Minimum Salary: {minimum_salary}; Workplace Type: {workplace_type}; Experience Level: {experience_level}; Employment Type: {employment_type}"

@app.get("/analytics")
def analytics():
    analytics_data = load_analytics_data()

    return render_template(                         # return 把生成好的页面发送给浏览器
        "analytics.html",
        analytics=analytics_data
    )

@app.get("/analytics/charts/<filename>")
def analytics_chart(filename):
    allowed_files = {
        "workplace_type_analytics_chart.png",
        "employment_type_analytics_chart.png",
        "experience_level_analytics_chart.png"
    }

    if filename not in allowed_files:
        abort(404)

    chart_directory = Path(app.root_path) / "analytics"   # 是 Flask 应用代码所在的磁盘文件夹。E:\Project_1\analytics

    return send_from_directory(chart_directory, filename)  # E:\Project_1\analytics

@app.get("/policies")
def policies():
    return render_template("policies.html")

if __name__ == "__main__":
    app.run(debug=True)       #Flask 的 .run() 方法。启动网页用的才是 app.run(...)。
