from flask import Flask, render_template, request, jsonify, abort
from recommendation_service import clean_text_list, recommend_jobs, EDUCATION_RANKS
from skill_normalizer import all_skills, find_skill_suggestions, return_suggestions
from database import get_database_connection
from routes import fetch_country_subdivision, fetch_nearby_places, fetch_country_id
import math
app = Flask(__name__)    #Create Flask application object, the entire backend program.
@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/skills")
def api_skills():
    skill_text = request.args.get("q", "").strip()     # like a dictionary {"q" : value}

    if len(skill_text) < 2 or len(skill_text) > 100:
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
    subdivision_data = fetch_country_subdivision(latitude, longitude)
    nearby_data = fetch_nearby_places(latitude, longitude)
    if subdivision_data is None or "status" in subdivision_data:
        return jsonify({"error": "Could not fetch country and province"}), 502

    if (not isinstance(nearby_data, dict) or "status" in nearby_data or not isinstance(nearby_data.get("geonames"), list)):
        print("Nearby lookup failed:", nearby_data)
        nearby_data = {"geonames": []}

    country = subdivision_data.get("countryName")
    country_code = subdivision_data.get("countryCode")
    country_id = fetch_country_id(country_code)
    if country_id is None:
        return jsonify({"error": "Could not fetch country ID"}), 502

    location_options.append({
        "type": "country",
        "name": country,
        "id": country_id,
        "country_id": country_id,
    })

    province = subdivision_data.get("adminName1")
    province_id = subdivision_data.get("admin1geonameId")

    if province is not None and province_id is not None:
        location_options.append({
            "type": "province",
            "name": f"{province}, {country}",
            "id": province_id,
            "country_id": country_id,
        })

    for place in nearby_data["geonames"]:
        if place.get("countryCode") != country_code:
            continue

        city = place["name"]
        province = place.get("adminName1")
        geoname_id = place["geonameId"]

        parts = []
        for value in (city, province, country):
            if value:
                parts.append(value)

        location_options.append({
            "type": "city",
            "name": ", ".join(parts),
            "id": geoname_id,
            "country_id": country_id,
        })

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
    experience_level = request.form["experience_level"]
    employment_type = request.form["employment_type"]
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
        "experience_levels": [experience_level],
        "workplace_types": [workplace_type],
        "employment_types": [employment_type],
        "education_level": education_level,
        "salary_currency": salary_currency,
        "location_id": location_id,
        "location_type": location_type,
        "location_country_id": location_country_id,
    }
    recommendations = recommend_jobs(user_preferences)
    return render_template(
        "results.html",
        recommendations=recommendations,
        user_preferences=user_preferences
    )

# return f"Skills: {skills}; Locations: {locations}; Minimum Salary: {minimum_salary}; Workplace Type: {workplace_type}; Experience Level: {experience_level}; Employment Type: {employment_type}"


if __name__ == "__main__":
    app.run(debug=True)       #Flask 的 .run() 方法。启动网页用的才是 app.run(...)。
