from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.auth_service import login, register

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
def register_api(data: RegisterRequest):

    user = register(
        data.username,
        data.password
    )

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    return {
        "message": "Register success"
    }


@router.post("/login")
def login_api(data: LoginRequest):

    result = login(
        data.username,
        data.password
    )

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return result