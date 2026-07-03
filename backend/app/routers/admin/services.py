from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.dependencies import require_admin
from app.services.admin.service_service import (
    get_all_services,
    get_service_by_id,
    create_service,
    update_service,
    delete_service
)

router = APIRouter(
    prefix="/admin/services",
    tags=["Admin - Services"],
    dependencies=[Depends(require_admin)]
)


class ServiceRequest(BaseModel):
    name: str
    description: str
    price: float
    duration_minutes: int


@router.get("")
def list_services():
    return get_all_services()


@router.get("/{service_id}")
def get_one(service_id: int):

    service = get_service_by_id(service_id)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


@router.post("")
def create(data: ServiceRequest):

    return create_service(
        data.name,
        data.description,
        data.price,
        data.duration_minutes
    )


@router.put("/{service_id}")
def update(service_id: int, data: ServiceRequest):

    service = update_service(service_id, data.dict())

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


@router.delete("/{service_id}")
def delete(service_id: int):

    service = delete_service(service_id)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return {"message": "Service deleted successfully"}
