from fastapi import APIRouter
from app.api.routers.user import user_router
from app.api.routers.documents import document_router

router = APIRouter()

router.include_router(user_router)
router.include_router(document_router)


