from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError

from app.services.auth_service import SECRET_KEY, ALGORITHM


def get_current_user(authorization: str = Header(...)):
    """Decode JWT token from the Authorization header and return its payload."""

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header"
        )

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload


def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency that only allows users with role == 'Admin'."""

    if current_user.get("role") != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )

    return current_user
