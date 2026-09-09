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

response = requests.patch(
    f"{BASE}/users/password",
    headers={
        "Authorization": f"Bearer {token}"
    },
    json={
        "current_password": "AIWorkspace@123",
        "new_password": "NewPassword@456",
    },
)

print(response.status_code)
print(response.json())