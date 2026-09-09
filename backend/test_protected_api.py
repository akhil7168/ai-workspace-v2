import requests

BASE_URL = "http://127.0.0.1:8000"

# Login first
login = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "akhil@example.com",
        "password": "AIWorkspace@123"
    }
)

tokens = login.json()

access_token = tokens["access_token"]

response = requests.get(
    f"{BASE_URL}/users/me",
    headers={
        "Authorization": f"Bearer {access_token}"
    }
)

print(response.status_code)
print(response.json())