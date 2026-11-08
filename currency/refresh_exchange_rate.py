import requests
import json
from pathlib import Path

SEARCH_EXCHANGE_RATE_PATH = Path(__file__).with_name("exchange_rates_cache.json")      #
TEM_SEARCH_EXCHANGE_RATE_PATH = Path(__file__).with_name("tem_exchange_rates_cache.json")

API_URL = "https://api.frankfurter.dev/v2/rates"

def fetch_exchange_rates():
    try:
        response = requests.get(API_URL, params={
        "base": "EUR",
        "providers": "ecb",
    },timeout = 15)
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError) as error:
        print(f"Could not get exchange rate: {error}")
        return None
    with TEM_SEARCH_EXCHANGE_RATE_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)

    TEM_SEARCH_EXCHANGE_RATE_PATH.replace(SEARCH_EXCHANGE_RATE_PATH)
    return data


if __name__ == "__main__":
    fetch_exchange_rates()