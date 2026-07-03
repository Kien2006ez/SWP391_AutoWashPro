from fastapi import APIRouter, Depends

from app.dependencies import require_admin
from app.services.admin.dashboard_service import get_dashboard_stats

router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Admin - Dashboard"],
    dependencies=[Depends(require_admin)]
)


@router.get("/stats")
def stats():
    return get_dashboard_stats()
