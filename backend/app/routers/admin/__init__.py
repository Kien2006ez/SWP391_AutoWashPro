from fastapi import APIRouter

from app.routers.admin.dashboard import router as dashboard_router
from app.routers.admin.users import router as users_router
from app.routers.admin.bookings import router as bookings_router
from app.routers.admin.services import router as services_router
from app.routers.admin.promotions import router as promotions_router

router = APIRouter()

router.include_router(dashboard_router)
router.include_router(users_router)
router.include_router(bookings_router)
router.include_router(services_router)
router.include_router(promotions_router)