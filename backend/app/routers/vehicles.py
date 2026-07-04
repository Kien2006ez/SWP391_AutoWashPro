from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_customer
from app.models.customer import Customer, CustomerVehicle
from app.schemas.customer_schema import VehicleCreate, VehicleResponse

router = APIRouter()

MAX_VEHICLES = 3  # BR-06


@router.get("", response_model=list[VehicleResponse])
def list_vehicles(customer: Customer = Depends(get_current_customer)):
    """Xem danh sách xe đã liên kết."""
    return customer.vehicles


@router.post("", response_model=VehicleResponse, status_code=201)
def add_vehicle(
    payload: VehicleCreate,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """FR-03: Liên kết biển số xe."""
    # BR-06: tối đa 3 xe
    if len(customer.vehicles) >= MAX_VEHICLES:
        raise HTTPException(
            status_code=400,
            detail=f"Tối đa {MAX_VEHICLES} xe mỗi tài khoản.",
        )
    # BR-07: biển số không được trùng
    existing = (
        db.query(CustomerVehicle)
        .filter(CustomerVehicle.license_plate == payload.license_plate)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Biển số này đã được liên kết với tài khoản khác.",
        )

    vehicle = CustomerVehicle(
        customer_id=customer.customer_id,
        license_plate=payload.license_plate,
        vehicle_type=payload.vehicle_type,
        brand=payload.brand,
        is_primary=payload.is_primary or len(customer.vehicles) == 0,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=204)
def remove_vehicle(
    vehicle_id: UUID,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db),
):
    """Xóa xe khỏi tài khoản."""
    vehicle = (
        db.query(CustomerVehicle)
        .filter(
            CustomerVehicle.vehicle_id == vehicle_id,
            CustomerVehicle.customer_id == customer.customer_id,
        )
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Xe không tìm thấy.")
    db.delete(vehicle)
    db.commit()
    return None