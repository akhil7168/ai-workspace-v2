import requests

BASE_URL = "http://127.0.0.1:8000"

payload = {
    "full_name": "Akhil Reddy",
    "email": "akhil@example.com",
    "password": "AIWorkspace@123"
}

response = requests.post(
    f"{BASE_URL}/auth/register",
    json=payload
)

print(response.status_code)
print(response.json())

login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": payload["email"],
        "password": payload["password"]
    }
)

print(login.status_code)
print(login.json())