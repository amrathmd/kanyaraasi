# fastapi
import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from sqlalchemy.orm import Session

from datetime import datetime


from app.api.endpoints.document.function import get_month, generate_presigned_url, create_document_inprogress, \
    update_document_status_util, get_document_by_id, get_current_month_docs, build_object_key
from app.api.endpoints.user import functions as user_functions
from app.core.dependencies import get_db
from app.schemas.account import AccountUpdate,AccountCreate,AccountResponse
from app.models.account import Account

from app.schemas.user import MyUser, User

bucket_name = "kanyaraasi-hugohub"
account_module = APIRouter()

@account_module.post("/accounts/{user_id}/{year}")
async def create_account(
        user_id: str,
        year: str,
        account_create: AccountCreate,
        db: Session = Depends(get_db)
):
    """
    Creates a new account entry for a user and year if it doesn't already exist.
    """
    existing_account = db.query(Account).filter(Account.user_id == user_id, Account.year == year).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Account already exists")

    new_account = Account(
        user_id=user_id,
        year=year,
        total_balance=account_create.total_balance,
        available_balance=account_create.available_balance
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return AccountResponse.from_orm(new_account)

# Optional: Endpoint to get account details (for verification)
@account_module.get("/account-details", response_model=AccountResponse)
async def get_account(current_user: Annotated[User, Depends(user_functions.get_current_user)], db: Session = Depends(get_db)):
    """
    Retrieves account details for a specific user and year.
    """
    account = db.query(Account).filter(Account.user_id == current_user.id, Account.year == str(datetime.now().year)).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account