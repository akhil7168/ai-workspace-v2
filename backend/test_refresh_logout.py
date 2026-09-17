from app.core.security import create_refresh_token

refresh = create_refresh_token()

print("Generated Refresh Token:")
print(refresh)

print("Length:", len(refresh))