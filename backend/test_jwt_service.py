from app.services.token_service import TokenService

token = TokenService.create_access_token(
    user_id="12345",
    email="akhil@example.com"
)

print(token)

decoded = TokenService.decode_token(token)

print(decoded)