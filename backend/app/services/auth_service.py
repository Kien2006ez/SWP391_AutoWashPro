from datetime import datetime, timedelta
from jose import jwt

# JWT Configuration
SECRET_KEY = "autowashpro2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2


users = [
    {
        "id": 1,
        "username": "admin",
        "password": "123456",
        "role": "Admin"
    }
]


def create_access_token(username: str, role: str):
    """Generate JWT access token"""

    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def register(username: str, password: str):
    """Register new user"""

    for user in users:
        if user["username"] == username:
            return None

    new_user = {
        "id": len(users) + 1,
        "username": username,
        "password": password,
        "role": "Customer"
    }

    users.append(new_user)

    return {
        "id": new_user["id"],
        "username": new_user["username"],
        "role": new_user["role"]
    }


def login(username: str, password: str):
    """Authenticate user"""

    for user in users:

        if (
            user["username"] == username
            and user["password"] == password
        ):

            token = create_access_token(
                username=user["username"],
                role=user["role"]
            )

            return {
                "message": "Login successful",
                "token": token,
                "username": user["username"],
                "role": user["role"]
            }

    return None