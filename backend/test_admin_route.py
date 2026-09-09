import requests

BASE = "http://127.0.0.1:8000"

login = requests.post(
    f"{BASE}/auth/login",
    json={
        "email":"akhil@example.com",
        "password":"NewPassword@456"
    }
)

token = login.json()["access_token"]

response = requests.get(
    f"{BASE}/users/admin-only",
    headers={
        "Authorization":f"Bearer {token}"
    }
)

print(response.status_code)
print(response.json())