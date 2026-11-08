import requests


url = "https://www.ualberta.ca/en/index.html"

response = requests.get(url, timeout = 10)

print(response.url)
print(response.text)
print(response.status_code)
if response.status_code == 200:
    print("Request successful")
    print(response.text)
else:
    print("Request failed")