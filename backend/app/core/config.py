"""
Application configuration.
Owner: M5 (Database Designer) / M3 (Backend)

Loads settings from environment variables (.env file).
Every other file imports `settings` from here instead of reading
os.environ directly, so config stays in one place.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/autowash"

    # ── JWT Auth ─────────────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ── OTP ──────────────────────────────────────────────────
    OTP_EXPIRE_MINUTES: int = 5
    OTP_RATE_LIMIT_PER_HOUR: int = 5

    # ── SMS (mock for prototype; replace with real provider later) ──
    SMS_PROVIDER: str = "mock"  # "mock" prints to console instead of sending
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""

    # ── App ──────────────────────────────────────────────────
    APP_NAME: str = "AutoWash Pro API"
    DEBUG: bool = True
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5500"]

    class Config:
        env_file = ".env"


settings = Settings()