from fastapi import FastAPI
from app.routers import admin  

app = FastAPI(title="AutoWashPro API")

app.include_router(admin.router) 