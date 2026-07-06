from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        routes=app.routes,
    )
    # Thêm HTTPBearer scheme để Swagger hiện ô nhập token
    schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    # Áp dụng cho tất cả endpoint
    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


@app.get("/")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


# ── Routers ──────────────────────────────────────────────────
from app.routers import auth
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

from app.routers import vehicles
app.include_router(vehicles.router, prefix="/api/customers/me/vehicles", tags=["vehicles"])

from app.routers import bookings
app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])

from app.routers import loyalty
app.include_router(loyalty.router, prefix="/api/loyalty", tags=["loyalty"])

from app.routers import admin
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

from app.routers import promotions
app.include_router(promotions.router, prefix="/api/admin/promotions", tags=["promotions"])

from app.routers import research
app.include_router(research.router, prefix="/api/admin", tags=["research"])


# ── Cron Jobs ─────────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    from app.jobs.scheduler import start_scheduler
    start_scheduler()