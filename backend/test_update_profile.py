import requests

BASE = "http://127.0.0.1:8000"

login = requests.post(
    f"{BASE}/auth/login",
    json={
        "email": "akhil@example.com",
        "password": "AIWorkspace@123",
    },
)

token = login.json()["access_token"]

response = requests.put(
    f"{BASE}/users/profile",
    headers={
        "Authorization": f"Bearer {token}"
    },
    json={
        "full_name": "Akhil Sai Reddy"
    },
)

print(response.status_code)
print(response.json())