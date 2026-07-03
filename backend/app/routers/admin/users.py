from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.dependencies import require_admin
from app.services.admin.user_service import (
    get_all_users,
    get_user_by_id,
    update_user_role,
    update_user_status,
    delete_user
)

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - Users"],
    dependencies=[Depends(require_admin)]
)


class RoleUpdateRequest(BaseModel):
    role: str


class StatusUpdateRequest(BaseModel):
    status: str


@router.get("")
def list_users():
    return get_all_users()


@router.get("/{user_id}")
def get_user(user_id: int):

    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.put("/{user_id}/role")
def change_role(user_id: int, data: RoleUpdateRequest):

    user = update_user_role(user_id, data.role)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.put("/{user_id}/status")
def change_status(user_id: int, data: StatusUpdateRequest):

    user = update_user_status(user_id, data.status)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.delete("/{user_id}")
def remove_user(user_id: int):

    success = delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {"message": "User deleted successfully"}
