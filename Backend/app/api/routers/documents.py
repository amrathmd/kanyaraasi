from fastapi import APIRouter
from app.api.endpoints.document.documents import document_module
document_router = APIRouter()

document_router.include_router(
    document_module,
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)