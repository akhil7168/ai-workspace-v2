from app.core.security import create_refresh_token

token = create_refresh_token()

print("Refresh Token Length:", len(token))
print("Token:", token[:20], "...")