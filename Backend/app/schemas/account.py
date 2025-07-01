# account.py
# Pydantic schemas for account-related data validation and serialization.

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal # For precise representation of currency

# --- Base Account Schema ---
# Not strictly necessary here as creation and response are quite different,
# but can be useful if more shared fields emerge.

# --- Schema for Creating an Account ---

class AccountCreate(BaseModel):
    """
    Schema for creating a new account record for a user for a specific year.
    """
    user_id: str = Field(..., example="user_uuid_or_string_id", description="Identifier of the user this account belongs to.")
    year: str = Field(..., example="2023", pattern=r"^\d{4}$", description="The financial year for this account (e.g., '2023').")
    total_balance: Decimal = Field(..., decimal_places=2, example=Decimal("1000.00"), description="Total allocated balance for the year.")
    available_balance: Optional[Decimal] = Field(None, decimal_places=2, example=Decimal("800.50"), description="Currently available balance for the year. Defaults to total_balance if not provided.")

    # If available_balance is not provided, it could default to total_balance.
    # This logic would typically be handled in the API endpoint/service layer.

# --- Schema for Updating an Account ---

class AccountUpdate(BaseModel):
    """
    Schema for updating an existing account's available balance.
    Typically, only the available_balance is mutable after creation through regular operations.
    Total balance might be adjusted by admin actions.
    """
    available_balance: Decimal = Field(..., decimal_places=2, example=Decimal("750.00"), description="The new available balance for the account.")
    # Add other fields here if they are updatable, e.g., total_balance for admin adjustments.
    # is_active: Optional[bool] = Field(None, description="Set account active or inactive (soft delete).")


# --- Schema for Account Response ---

class AccountResponse(BaseModel):
    """
    Schema for representing an account in API responses.
    Includes fields from CommonModel (id, is_active, created_at, updated_at).
    """
    id: int = Field(..., example=1, description="Unique identifier of the account record.")
    user_id: str = Field(..., example="user_uuid_or_string_id", description="Identifier of the user this account belongs to.")
    year: str = Field(..., example="2023", description="The financial year of this account record.")
    total_balance: Decimal = Field(..., decimal_places=2, example=Decimal("1000.00"), description="Total allocated balance for the year.")
    available_balance: Decimal = Field(..., decimal_places=2, example=Decimal("800.50"), description="Currently available balance for the year.")

    is_active: bool = Field(..., description="Indicates if the account record is active.")
    created_at: datetime = Field(..., description="Timestamp of when the account record was created.")
    updated_at: datetime = Field(..., description="Timestamp of when the account record was last updated.")

    class Config:
        # For Pydantic V2, use `from_attributes = True`
        orm_mode = True
        # Pydantic V2 also supports arbitrary_types_allowed for Decimal, but explicit is better.
        # For Pydantic V1, ensure Decimals are handled correctly, sometimes they need json_encoders.
        # However, FastAPI/Starlette usually handle Decimal serialization to string by default.