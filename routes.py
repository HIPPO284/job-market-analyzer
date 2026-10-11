import requests

COUNTRY_SUBDIVISION_URL = "https://secure.geonames.org/countrySubdivisionJSON"
NEARBY_PLACES_URL = "https://secure.geonames.org/findNearbyJSON"
COUNTRY_INFO_URL = "https://secure.geonames.org/countryInfoJSON"

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

def fetch_nearby_places(latitude, longitude):
    params = {
        "lat": latitude,
        "lng": longitude,
        "username": "wukuncheng",
        "lang": "en",
        "radius": 200,
        "maxRows": 8,
        "featureClass": "P",
    }
    try:
        response = requests.get(NEARBY_PLACES_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Could not fetch nearby places: {error}")
        return None
    return data


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