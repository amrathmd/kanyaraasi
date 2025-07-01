# auth.py
# API endpoints for user authentication (login, signup) and profile retrieval.

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated # For Depends with type hints
from datetime import timedelta

from sqlalchemy.orm import Session

# Updated schema imports
from app.schemas.user import LoginRequest, UserCreate, UserPublic, Token
from app.core.dependencies import get_db
from app.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES # REFRESH_TOKEN_EXPIRE_DAYS not used here currently
from app.api.endpoints.user import functions as user_crud_functions # Renamed for clarity (CRUD + auth functions)
# Assuming user_functions is now user_crud_functions and contains the necessary logic.

auth_module = APIRouter(
    tags=["Authentication"], # Group endpoints in OpenAPI docs
    responses={404: {"description": "Not found"}} # Default response for this router
)


@auth_module.post(
    "/login",
    response_model=Token,
    summary="User Login",
    description="Authenticate a user and receive an access token."
)
async def login_for_access_token(
    login_request: LoginRequest, # Use new schema LoginRequest
    db: Session = Depends(get_db)
) -> Token:
    """
    Handles user login.
    - Authenticates the user based on email and password.
    - If successful, creates and returns an access token.
    - Raises HTTPException 401 if authentication fails.
    """
    # user_functions.authenticate_user likely returns a User model instance or None
    authenticated_user = user_crud_functions.authenticate_user(db, user_credentials=login_request)

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password", # More generic message often preferred
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Ensure the data passed to create_access_token matches what it expects.
    # The User model (SQLAlchemy) now has 'id', 'email', 'role'.
    token_data = {"id": str(authenticated_user.id), "email": authenticated_user.email, "role": authenticated_user.role.value} # role.value if role is an Enum

    access_token = user_crud_functions.create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )

    # The Token schema was refactored. It no longer includes 'role' directly.
    # If 'role' is needed in the response, the Token schema should be adjusted,
    # or it should be part of the token claims.
    return Token(access_token=access_token, token_type="bearer")


@auth_module.post(
    "/signup",
    response_model=UserPublic, # Return the created user's public representation
    status_code=status.HTTP_201_CREATED, # Set appropriate status code for creation
    summary="User Signup",
    description="Register a new user in the system."
)
async def signup(
        user_to_create: UserCreate, # Use new schema UserCreate
        db: Session = Depends(get_db)
) -> UserPublic:
    """
    Handles new user registration (signup).
    - Checks if a user with the given email already exists.
    - Creates a new user if email is not taken.
    - Returns the created user's public information.
    """
    # user_crud_functions.signup_user should now:
    # 1. Check for existing user by email.
    # 2. Create the user using UserCreate schema.
    # 3. Return the created User SQLAlchemy model instance.
    # An HTTPException (e.g., 400 or 409) should be raised from signup_user if email exists.

    created_user_model = user_crud_functions.signup_user(db=db, user_create_schema=user_to_create)

    # If signup_user raises HTTPException on error, no need to check return value here.
    # If it returns None on error (less ideal), then check:
    # if not created_user_model:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered or invalid data.")

    # Convert SQLAlchemy model to Pydantic schema for response
    return UserPublic.from_orm(created_user_model)


@auth_module.get(
    '/user/profile',
    response_model=UserPublic, # Use new schema UserPublic
    summary="Get Current User Profile",
    description="Retrieve the profile information of the currently authenticated user."
)
async def read_current_user_profile(
    current_user: Annotated[UserPublic, Depends(user_crud_functions.get_current_user)] # Type hint should be UserPublic
    # The get_current_user dependency should return a User model instance,
    # which FastAPI will convert to UserPublic based on response_model.
    # Or, get_current_user itself can return a UserPublic schema instance.
):
    """
    Retrieves the profile of the currently authenticated user.
    The `get_current_user` dependency handles token validation and fetching user data.
    """
    # current_user is already the correct type (User model instance or UserPublic schema instance)
    # due to the Depends and Annotated setup. FastAPI handles the conversion to response_model.
    return current_user