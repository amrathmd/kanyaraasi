# account.py
# API endpoints for managing user accounts.

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated # For Depends with type hints
from datetime import datetime
from decimal import Decimal # Ensure Decimal is imported if used directly

from sqlalchemy.orm import Session

# User-related imports
from app.api.endpoints.user import functions as user_crud_functions # Alias for user functions
from app.models.user import User as UserModel # For type hinting current_user

# Account-related imports
from app.core.dependencies import get_db
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate # Using refactored schemas
from app.models.account import Account as AccountModel # Explicit model import

# Unused imports from original file:
# import uuid
# import asyncio
# from app.api.endpoints.document.function import ... (multiple functions)
# from app.schemas.user import MyUser (deprecated)

# bucket_name = "kanyaraasi-hugohub" # This seems unused here, consider removing or moving to settings

account_module = APIRouter(
    prefix="/accounts",  # Standard prefix for account-related endpoints
    tags=["Accounts"],    # Tag for OpenAPI documentation
    responses={
        404: {"description": "Account not found"},
        403: {"description": "Operation not permitted"},
        401: {"description": "Not authenticated"}
    }
)

# Define a version of AccountCreate that doesn't require user_id and year, as they come from path
class AccountCreateBody(BaseModel):
    total_balance: Decimal = Field(..., decimal_places=2, description="Total allocated balance.")
    available_balance: Optional[Decimal] = Field(None, decimal_places=2, description="Available balance, defaults to total if None.")

@account_module.post(
    "/{user_id}/{year}",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User Account for a Year",
    description="Creates a new account entry for a specified user and year if it doesn't already exist."
)
async def create_user_account_for_year(
        user_id: str,
        year: str, # Consider adding regex validation for year format if not in schema
        account_data: AccountCreateBody, # Use the specialized body schema
        db: Session = Depends(get_db)
) -> AccountResponse:
    """
    Creates an account for a given `user_id` and `year`.
    - `user_id`: The ID of the user (string).
    - `year`: The financial year (string, e.g., "2023").
    - `account_data`: Contains `total_balance` and optional `available_balance`.

    Raises HTTPException 400 if the account already exists.
    Raises HTTPException 404 if the user does not exist (optional check).
    """
    # Optional: Validate if the user_id exists
    # user = user_crud_functions.get_user_by_id(db, user_id=user_id)
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found.")

    existing_account = db.query(AccountModel).filter(
        AccountModel.user_id == user_id,
        AccountModel.year == year
    ).first()

    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account for user {user_id} in year {year} already exists."
        )

    # Determine available_balance if not provided
    available_balance = account_data.available_balance if account_data.available_balance is not None else account_data.total_balance

    new_account = AccountModel(
        user_id=user_id,
        year=year,
        total_balance=account_data.total_balance, # Already Decimal from schema
        available_balance=available_balance      # Already Decimal
        # id, is_active, created_at, updated_at are handled by CommonModel
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return AccountResponse.from_orm(new_account)


@account_module.get(
    "/me/{year}",
    response_model=AccountResponse,
    summary="Get Current User's Account for a Year",
    description="Retrieves account details for the currently authenticated user for a specific year."
)
async def get_my_account_for_year(
    year: str, # Path parameter for year
    current_user: Annotated[UserModel, Depends(user_crud_functions.get_current_user)], # UserModel from Depends
    db: Session = Depends(get_db)
) -> AccountResponse:
    """
    Retrieves account details for the currently authenticated user for the specified `year`.
    Raises HTTPException 404 if the account is not found for that user and year.
    """
    account = db.query(AccountModel).filter(
        AccountModel.user_id == current_user.id, # current_user.id is a string
        AccountModel.year == year
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account not found for year {year} for the current user."
        )
    return AccountResponse.from_orm(account)

# Placeholder for other account endpoints:
# GET /admin/{user_id}/{year} - Admin get specific user account
# PUT /me/{year} or /admin/{user_id}/{year} - Update account (e.g. available_balance using AccountUpdate schema)

# Original endpoint "/account-details" was less RESTful.
# Replaced with "/me/{year}" for current user's specific year account.
# An admin endpoint could be "/{user_id}/{year}"