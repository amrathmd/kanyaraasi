from fastapi import APIRouter
from app.api.endpoints.account.account import account_module

account_router = APIRouter()

account_router.include_router(
    account_module,
    prefix="/account",
    tags=["account"],
    responses={404: {"description": "Not found"}},
)