from pydantic import BaseModel, Field


class OtpRequestPayload(BaseModel):
    phone_number: str = Field(..., min_length=9, max_length=15)


class OtpRequestResponse(BaseModel):
    message: str
    expires_in_minutes: int


class LoginRequest(BaseModel):
    phone_number: str = Field(..., min_length=9, max_length=15)
    otp_code: str = Field(..., min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminLoginRequest(BaseModel):
    username: str
    password: str