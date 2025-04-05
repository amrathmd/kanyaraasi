from fastapi import APIRouter
from app.api.endpoints.admin.admin import admin_module
admin_router = APIRouter()

admin_router.include_router(
    admin_module,
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)