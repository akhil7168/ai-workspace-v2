from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)

password = "AIWorkspace@123"

hashed = hash_password(password)

print("Hash OK:", hashed.startswith("$2"))

print(
    "Verify OK:",
    verify_password(password, hashed),
)

token = create_access_token(
    subject="akhil@example.com"
)

print("Token:", token[:25], "...")

decoded = decode_token(token)

print(decoded)