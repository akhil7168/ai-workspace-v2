from app.core.security import (
    hash_password,
    verify_password
)

password = "AIWorkspace@123"

hashed = hash_password(password)

print("Original :", password)
print("Hashed   :", hashed)

print(
    verify_password(password, hashed)
)

print(
    verify_password("wrongpassword", hashed)
)