# user.py
# API endpoints for user management (e.g., listing users, getting user details).
# These endpoints are typically protected and may require specific roles (e.g., admin).

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Annotated

from sqlalchemy.orm import Session

from app.core.dependencies import get_db # oauth2_scheme might be needed for protected routes
# Import get_current_user if these routes need to be protected
# from app.api.endpoints.user.functions import get_current_user
from app.api.endpoints.user import functions as user_crud_functions # Renamed for clarity
from app.schemas.user import UserPublic # Using the refactored UserPublic schema
from app.models.user import User as UserModel # For type hinting current_user if needed

# s3_utils are not used in these basic CRUD examples, so commenting out for now
# from app.utils.s3_utils import download_file_from_s3, upload_file_to_s3

user_module = APIRouter(
    prefix="/users",  # Prefix for all routes in this module
    tags=["Users"],      # Tag for OpenAPI documentation
    responses={
        404: {"description": "User not found"},
        # 403: {"description": "Operation not permitted"} # Example for permission errors
    }
)

@user_module.get(
    "/",
    response_model=List[UserPublic],
    summary="List All Users",
    description="Retrieve a list of all registered users. Typically an admin-only endpoint."
    # dependencies=[Depends(get_current_admin_user)] # Example for an admin protection dependency
)
async def read_users_list(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    db: Session = Depends(get_db)
) -> List[UserPublic]:
    """
    Retrieves a paginated list of users.

    *Note: This endpoint should be protected and accessible only by administrators.*
    """
    users = user_crud_functions.read_all_users(db, skip=skip, limit=limit)
    return [UserPublic.from_orm(user) for user in users]


@user_module.get(
    "/{user_id}",
    response_model=UserPublic,
    summary="Get User by ID",
    description="Retrieve details for a specific user by their ID."
    # dependencies=[Depends(get_current_active_user)] # Example: could be admin or the user themselves
)
async def read_user_by_id(
    user_id: str, # User ID is a string in the refactored User model
    db: Session = Depends(get_db)
    # current_user: Annotated[UserModel, Depends(get_current_user)] # Example if checking permissions
) -> UserPublic:
    """
    Retrieves a specific user by their unique ID.

    The user ID is expected to be the string representation (e.g., UUID).
    *Note: Access to this endpoint should be restricted (e.g., admin or the user themselves).*
    """
    db_user = user_crud_functions.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Example permission check (conceptual):
    # if not current_user.role == UserRole.ADMIN and current_user.id != db_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user")

    return UserPublic.from_orm(db_user)

# Further endpoints could be added here:
# - PUT /users/{user_id} (Update user)
# - DELETE /users/{user_id} (Delete user - admin)
# - PATCH /users/me (Update current user's profile)

