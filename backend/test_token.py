from app.core.security import create_access_token, decode_token

token = create_access_token("akhil@example.com")

print("TOKEN:")
print(token)

print("\nDECODED:")
print(decode_token(token))