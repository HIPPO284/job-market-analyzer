from unittest import case

import requests

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
    return data
exchange_rates = fetch_exchange_rates()

def convert_to_eur(amount, currency, exchange_rates):
    if amount is None or currency is None:
        return None
    if currency == "EUR":
        return amount
    if exchange_rates is None:
        return None
    for item in exchange_rates:
        if item["quote"] == currency:
            return amount / item["rate"]

def convert_to_input_currency(amount_eur, input_currency, exchange_rates):
    if amount_eur is None or input_currency is None:
        return None
    if input_currency == "EUR":
        return amount_eur
    if exchange_rates is None:
        return None
    for item in exchange_rates:
        if item["quote"] == input_currency:
            return amount_eur * item["rate"]

    return None






def calculate_annual_salary(amount, salary_period, working_hours_per_week=None, working_days_per_week=None):
    if amount is None or salary_period is None:
        return None

    match salary_period:
        case "annual":
            return amount
        case "monthly":
            return amount * 12
        case "weekly":
            return amount * 52
        case "biweekly":
            return amount * 26
        case "daily":
            if working_days_per_week is None:
                return amount * 5 * 52
            else:
                return amount * working_days_per_week * 52
        case "hourly":
            if working_hours_per_week is None:
                return amount * 40 * 52
            else:
                return amount * working_hours_per_week * 52
        case _:
            return None




                                              # 31200
if __name__ == "__main__":
    print(fetch_exchange_rates())
    print(calculate_annual_salary(1000, "weekly"))  # 52000
    print(calculate_annual_salary(2000, "biweekly"))  # 52000

    print(calculate_annual_salary(18, "hourly"))  # 37440
    print(calculate_annual_salary(18, "hourly", 20))  # 18720

    print(calculate_annual_salary(
        150, "daily", working_days_per_week=4
    ))