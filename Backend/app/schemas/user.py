# user.py
# Pydantic schemas for user-related data validation and serialization.

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.utils.constant.globals import UserRole # Defines the UserRole enum

# --- Base User Schemas ---

class UserBase(BaseModel):
    """
    Base schema for user attributes, shared by creation and read schemas.
    """
    email: EmailStr = Field(..., example="user@example.com", description="User's email address.")
    name: Optional[str] = Field(None, example="John Doe", description="User's full name or display name.")

    class Config:
        # For Pydantic V2, use `from_attributes = True` instead of `orm_mode = True`
        orm_mode = True


# --- Schemas for User Creation ---

class UserCreate(UserBase):
    """
    Schema for creating a new user (e.g., during signup).
    Includes password which is not present in read schemas.
    """
    password: str = Field(..., min_length=8, example="strongpassword123", description="User's password (min 8 characters).")
    # Role is typically assigned by the system or defaults, not usually part of signup by user.
    # If role can be specified at creation by an admin, it could be added here.


# --- Schemas for User Authentication ---

class LoginRequest(BaseModel):
    """
    Schema for user login request.
    """
    email: EmailStr = Field(..., example="user@example.com", description="User's email for login.")
    password: str = Field(..., example="password123", description="User's password for login.")


# --- Schemas for Representing Existing Users (Read Schemas) ---

class UserPublic(UserBase):
    """
    Schema for representing a user's public information.
    This is typically used in API responses.
    """
    id: str = Field(..., example="user_uuid_or_string_id", description="Unique identifier of the user.")
    role: UserRole = Field(..., example=UserRole.USER, description="Role of the user.")
    is_active: Optional[bool] = Field(True, description="Whether the user account is active.")
    created_at: Optional[datetime] = Field(None, description="Timestamp of user creation.")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of last user update.")

    # Note: The 'id' type (str) should match the User SQLAlchemy model's id type.
    # The User model was refactored to have a String id.
    # CommonModel fields like is_active, created_at, updated_at are now included.

# Renamed 'User' to 'UserPublic' for clarity.
# Renamed 'MyUser' to 'UserCreate' and made 'UserBase' for shared fields.

# --- Schemas for Tokens ---

class Token(BaseModel):
    """
    Schema for representing JWT access and refresh tokens.
    """
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", description="JWT access token.")
    token_type: str = Field("bearer", example="bearer", description="Type of the token (typically 'bearer').")
    # role: UserRole = Field(..., description="Role of the user associated with the token.")
    # Role is often embedded in the token claims rather than returned alongside it this way.
    # If it's part of the token response payload, it can be kept.
    # For now, commenting it out as it's more common to get role from token claims after decoding.

class TokenData(BaseModel):
    """
    Schema for data embedded within a JWT token (e.g., user ID).
    """
    id: Optional[str] = Field(None, example="user_uuid_or_string_id", description="User ID extracted from token.")
    email: Optional[EmailStr] = Field(None, example="user@example.com", description="User email extracted from token.")
    role: Optional[UserRole] = Field(None, description="User role extracted from token.")

# Original Schemas for reference:
# class Login(BaseModel):
# 	email : str
# 	password : str

# class MyUser(BaseModel): # Renamed to UserCreate
# 	email : str
# 	password : str
# 	name: str

# class User(MyUser): # Renamed to UserPublic, inherits UserBase
# 	id :str
# 	role: UserRole

# class Token(BaseModel):
# 	access_token : str
# 	token_type : str
# 	role : UserRole # Commented out, see note above

