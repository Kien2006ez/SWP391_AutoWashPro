from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.customer import Customer
from app.models.admin_user import AdminUser

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/login",
    auto_error=False
)


def _decode_or_401(token: str | None) -> dict:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload


def get_current_customer(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Customer:
    payload = _decode_or_401(token)
    if payload.get("role") != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required"
        )
    customer = db.query(Customer).filter(
        Customer.customer_id == UUID(payload["sub"])
    ).first()
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer not found"
        )
    return customer


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    payload = _decode_or_401(token)
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    admin = db.query(AdminUser).filter(
        AdminUser.admin_id == UUID(payload["sub"])
    ).first()
    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found or inactive"
        )
    return admin