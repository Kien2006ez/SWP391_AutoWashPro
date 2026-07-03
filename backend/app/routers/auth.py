import random
import string
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import create_access_token, verify_password
from app.core.deps import get_current_customer
from app.core.config import settings
from app.models.customer import Customer
from app.models.otp import OtpRequest
from app.models.admin_user import AdminUser
from app.schemas.auth_schema import (
    OtpRequestPayload, OtpRequestResponse,
    LoginRequest, TokenResponse, AdminLoginRequest,
)
from app.schemas.customer_schema import (
    CustomerRegisterRequest, CustomerResponse, CustomerUpdateRequest,
)
from app.services.notification_service import send_sms

router = APIRouter()


def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def _verify_otp(db: Session, phone_number: str, otp_code: str) -> bool:
    otp = (
        db.query(OtpRequest)
        .filter(
            OtpRequest.phone_number == phone_number,
            OtpRequest.otp_code == otp_code,
            OtpRequest.is_used == False,
            OtpRequest.expires_at >= datetime.utcnow(),
        )
        .order_by(OtpRequest.created_at.desc())
        .first()
    )
    if otp is None:
        return False
    otp.is_used = True
    db.commit()
    return True


@router.post("/otp/request", response_model=OtpRequestResponse)
def request_otp(payload: OtpRequestPayload, db: Session = Depends(get_db)):
    # BR-05: rate limit 5 OTP per phone per hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent = (
        db.query(OtpRequest)
        .filter(
            OtpRequest.phone_number == payload.phone_number,
            OtpRequest.created_at >= one_hour_ago,
        )
        .count()
    )
    if recent >= settings.OTP_RATE_LIMIT_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Try again later.",
        )

    code = _generate_otp()
    otp = OtpRequest(
        phone_number=payload.phone_number,
        otp_code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
    )
    db.add(otp)
    db.commit()
    send_sms(payload.phone_number, f"Ma xac thuc AutoWash Pro: {code}")
    return OtpRequestResponse(
        message="OTP sent.",
        expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
    )


@router.post("/register", response_model=CustomerResponse, status_code=201)
def register(payload: CustomerRegisterRequest, db: Session = Depends(get_db)):
    # BR-01: phone must be unique
    if db.query(Customer).filter(Customer.phone_number == payload.phone_number).first():
        raise HTTPException(status_code=400, detail="Phone number already registered.")

    if not _verify_otp(db, payload.phone_number, payload.otp_code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    customer = Customer(
        phone_number=payload.phone_number,
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    send_sms(payload.phone_number, "Chao mung den voi AutoWash Pro!")
    return customer


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(
        Customer.phone_number == payload.phone_number
    ).first()
    if not customer:
        raise HTTPException(status_code=401, detail="Account not found.")
    if not _verify_otp(db, payload.phone_number, payload.otp_code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    token = create_access_token(str(customer.customer_id), role="customer")
    return TokenResponse(access_token=token)


@router.post("/admin/login", response_model=TokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    # BR-35: separate admin login
    admin = db.query(AdminUser).filter(
        AdminUser.username == payload.username
    ).first()
    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin account inactive.")
    token = create_access_token(str(admin.admin_id), role="admin")
    return TokenResponse(access_token=token)


@router.get("/me", response_model=CustomerResponse)
def get_me(customer: Customer = Depends(get_current_customer)):
    return customer


@router.patch("/me", response_model=CustomerResponse)
def update_me(
    payload: CustomerUpdateRequest,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    if payload.full_name is not None:
        customer.full_name = payload.full_name
    if payload.email is not None:
        customer.email = payload.email
    db.commit()
    db.refresh(customer)
    return customer