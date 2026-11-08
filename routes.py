import math

import requests

COUNTRY_SUBDIVISION_URL = "https://secure.geonames.org/countrySubdivisionJSON"
COUNTRY_INFO_URL = "https://secure.geonames.org/countryInfoJSON"
CITIES_URL = "https://secure.geonames.org/citiesJSON"
GEONAME_DETAILS_URL = "https://secure.geonames.org/getJSON"
CITY_SEARCH_RADIUS_KM = 200
MAX_CITY_OPTIONS = 8
# Keep country, province/state, and city-level options only. PPLA4 is a
# fourth-level administrative seat, so it is intentionally excluded.
CITY_SEAT_CODES = {"PPLC", "PPLA", "PPLA2", "PPLA3"}
CHINA_COUNTRY_ID = 1814991
CHINA_GROUP_COUNTRY_CODES = {"CN", "HK", "MO", "TW"}
CHINA_REGION_NAMES = {
    "HK": "Hong Kong",
    "MO": "Macau",
    "TW": "Taiwan",
}
SINGLE_CITY_REGIONS = {
    "HK": {"geoname_id": 1819729, "name": "Hong Kong"},
    "MO": {"geoname_id": 1821274, "name": "Macau"},
}


def country_group_code(country_code):
    normalized_code = (country_code or "").strip().upper()
    return "CN" if normalized_code in CHINA_GROUP_COUNTRY_CODES else normalized_code


def display_country(country_code, source_country_name):
    if country_group_code(country_code) == "CN":
        return "China", CHINA_COUNTRY_ID
    return source_country_name, fetch_country_id(country_code)

def fetch_country_subdivision(latitude, longitude):
    params = {
        "lat": latitude,
        "lng": longitude,
        "username": "wukuncheng",
        "lang": "en",
    }
    try:
        response = requests.get(
            COUNTRY_SUBDIVISION_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError)as error:
        print(f"Could not fetch country subdivision: {error}")
        return None
    return data

def fetch_nearby_cities(latitude, longitude, latitude_delta, longitude_delta):
    """Return cities from one GeoNames bounding-box request."""
    params = {
        "north": min(90, latitude + latitude_delta),
        "south": max(-90, latitude - latitude_delta),
        "east": min(180, longitude + longitude_delta),
        "west": max(-180, longitude - longitude_delta),
        "maxRows": 100,
        "username": "wukuncheng",
        "lang": "en",
    }
    try:
        response = requests.get(CITIES_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Could not fetch nearby cities: {error}")
        return None

    cities = data.get("geonames")
    return cities if isinstance(cities, list) else None


def city_distance_km(latitude, longitude, city):
    """Return the great-circle distance from the clicked point to a city."""
    try:
        city_latitude = float(city["lat"])
        city_longitude = float(city["lng"])
    except (KeyError, TypeError, ValueError):
        return math.inf

    earth_radius_km = 6371.0
    latitude_radians = math.radians(latitude)
    city_latitude_radians = math.radians(city_latitude)
    delta_latitude = city_latitude_radians - latitude_radians
    delta_longitude = math.radians(city_longitude - longitude)
    haversine = (
        math.sin(delta_latitude / 2) ** 2
        + math.cos(latitude_radians)
        * math.cos(city_latitude_radians)
        * math.sin(delta_longitude / 2) ** 2
    )
    return 2 * earth_radius_km * math.asin(math.sqrt(haversine))


def fetch_place_details(geoname_id):
    """Fetch the country and province that belong to one selected city."""
    try:
        response = requests.get(
            GEONAME_DETAILS_URL,
            params={
                "geonameId": geoname_id,
                "username": "wukuncheng",
                "lang": "en",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Could not fetch city details: {error}")
        return None

    return data if isinstance(data, dict) and "status" not in data else None


def find_nearby_formal_cities(latitude, longitude, selected_country_group):
    def valid_formal_cities(cities):
        return [
            city
            for city in cities or []
            if city.get("fcode") in CITY_SEAT_CODES
            and city.get("geonameId")
            and city_distance_km(latitude, longitude, city) <= CITY_SEARCH_RADIUS_KM
        ]

    # Ask for a compact box first. GeoNames limits a response to 100 rows and
    # can omit a nearby smaller city when a 200 km box contains many places.
    local_cities = valid_formal_cities(
        fetch_nearby_cities(latitude, longitude, 1.0, 1.0)
    )
    cities_by_id = {city["geonameId"]: city for city in local_cities}

    if len(cities_by_id) < MAX_CITY_OPTIONS:
        latitude_delta = CITY_SEARCH_RADIUS_KM / 111.0
        longitude_scale = max(math.cos(math.radians(latitude)), 0.01)
        longitude_delta = CITY_SEARCH_RADIUS_KM / (111.0 * longitude_scale)
        radius_cities = valid_formal_cities(
            fetch_nearby_cities(
                latitude,
                longitude,
                latitude_delta,
                longitude_delta,
            )
        )
        for city in radius_cities:
            cities_by_id.setdefault(city["geonameId"], city)

    formal_cities = list(cities_by_id.values())
    sorted_cities = sorted(
        formal_cities,
        key=lambda city: city_distance_km(latitude, longitude, city),
    )

    verified_cities = []
    for city in sorted_cities:
        details = fetch_place_details(city["geonameId"])
        if (
            not details
            or country_group_code(details.get("countryCode"))
            != selected_country_group
        ):
            continue

        verified_cities.append({
            **city,
            "adminName1": details.get("adminName1"),
            "countryCode": details.get("countryCode"),
        })
        if len(verified_cities) == MAX_CITY_OPTIONS:
            break

    return verified_cities


def build_location_options(latitude, longitude):
    subdivision_data = fetch_country_subdivision(latitude, longitude)
    if not isinstance(subdivision_data, dict) or "status" in subdivision_data:
        return None

    source_country = subdivision_data.get("countryName")
    country_code = subdivision_data.get("countryCode")
    selected_country_group = country_group_code(country_code)
    country, country_id = display_country(country_code, source_country)
    if not country or country_id is None:
        return None

    location_options = [{
        "type": "country",
        "name": country,
        "id": country_id,
        "country_id": country_id,
    }]

    province = CHINA_REGION_NAMES.get(
        (country_code or "").upper(),
        subdivision_data.get("adminName1"),
    )
    province_id = subdivision_data.get("admin1geonameId")
    is_single_city_region = (country_code or "").upper() in SINGLE_CITY_REGIONS
    if province and province_id and not is_single_city_region:
        location_options.append({
            "type": "province",
            "name": f"{province}, {country}",
            "id": province_id,
            "country_id": country_id,
        })

    cities = find_nearby_formal_cities(latitude, longitude, selected_country_group)
    if not cities and is_single_city_region:
        region = SINGLE_CITY_REGIONS[country_code.upper()]
        cities = [{
            "geonameId": region["geoname_id"],
            "name": region["name"],
            "adminName1": region["name"],
            "countryCode": country_code,
        }]

    for city in cities:
        city_name = city["name"]
        city_id = city["geonameId"]
        city_country_code = (city.get("countryCode") or "").upper()
        city_province = CHINA_REGION_NAMES.get(
            city_country_code,
            city.get("adminName1") or province,
        )
        city_country, _ = display_country(city_country_code, country)

        name_parts = [city_name]
        if city_province and city_province.casefold() != city_name.casefold():
            name_parts.append(city_province)
        name_parts.append(city_country)
        location_options.append({
            "type": "city",
            "name": ", ".join(name_parts),
            "id": city_id,
            "country_id": country_id,
        })

    return location_options


def fetch_country_id(country_code):
    if not country_code:
        return None

    country_code = country_code.strip().upper()
    params = {
        "country": country_code,
        "username": "wukuncheng",
        "lang": "en",
    }
    try:
        response = requests.get(
            COUNTRY_INFO_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Could not fetch country ID: {error}")
        return None

    if "status" in data or "error" in data:
        return None

    countries = data.get("geonames", [])

    if not countries:
        return None

    return countries[0].get("geonameId")



if __name__ == "__main__":
    latitude = 53.55014
    longitude = -113.46871

    subdivision_data = fetch_country_subdivision(latitude, longitude)
    print("Raw subdivision:", subdivision_data)

    assert isinstance(subdivision_data, dict) and "status" not in subdivision_data, "Subdivision query failed"

    country_code = subdivision_data.get("countryCode")
    country_name = subdivision_data.get("countryName")
    province_name = subdivision_data.get("adminName1")
    province_id = subdivision_data.get("admin1geonameId")

    country_id = fetch_country_id(country_code)

    print("Country:", country_name, country_code)
    print("Country ID:", country_id)
    print("Province:", province_name)
    print("Province ID:", province_id)

    assert country_code == "CA", "Expected Canada"
    assert province_name == "Alberta", "Expected Alberta"
    assert country_id == 6251999, "Incorrect Canada ID"
    assert province_id == 5883102, "Incorrect Alberta ID"

    print("Edmonton location test passed")
