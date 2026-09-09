import requests

BASE = "http://127.0.0.1:8000"

response = requests.post(
    f"{BASE}/auth/login",
    json={
        "email": "akhil@example.com",
        "password": "AIWorkspace@123",
    },
)

print(response.status_code)
print(response.json())