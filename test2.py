import os
from datetime import datetime, timedelta, timezone
from jose import jwt
import requests

# Step 1: Use the same secret and algorithm as in Vercel
SECRET_KEY = "7L7GXESrqhhdE9uOsX-XwE_Epvcv_1UWDDYd-7um0nE"
ALGORITHM = "HS256"  # make sure this matches Vercel

# Step 2: Generate a token
def create_access_token(user_id: str, email: str, expires_minutes: int = 60):
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode = {"user_id": user_id, "email": email, "exp": expire, "sub": "access"}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Replace with your test user info
token = create_access_token("test-user-id", "test.user@example.com")
print("Generated token:", token)

 
url = "https://fast-wallet-service.vercel.app/keys/create"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "accept": "application/json"
}

data = {
    "name": "Omah lay",
    "permissions": ["deposit", "transfer", "read"],
    "expiry": "1Y"
}

response = requests.post(url, headers=headers, json=data)

print("Status Code:", response.status_code)
print("Response Body:", response.json())