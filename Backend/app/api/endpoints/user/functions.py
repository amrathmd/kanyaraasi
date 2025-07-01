# functions.py (renamed from user_crud_functions for brevity if this file only contains user-related CRUD and auth logic)
# Business logic functions for user operations, including authentication,
# user creation, and profile management.

import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, List # Added List

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, oauth2_scheme
from app.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY # REFRESH_SECRET_KEY (not used yet)
from app.models import user as UserModel # Explicit import
from app.models.account import Account as AccountModel # Explicit import for account creation
from app.schemas.user import UserCreate, LoginRequest, TokenData, UserPublic # Updated schema imports
from app.utils.constant.globals import UserRole

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)


def get_user_by_email(db: Session, email: str) -> Optional[UserModel.User]:
    """
    Retrieves a user from the database by their email address.
    Returns the User model instance or None if not found.
    """
    return db.query(UserModel.User).filter(UserModel.User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[UserModel.User]: # Changed user_id to str
    """
    Retrieves a user from the database by their ID.
    The User model ID is a string.
    Returns the User model instance or None if not found.
    """
    # UserModel.User.id is a String type in the refactored model
    return db.query(UserModel.User).filter(UserModel.User.id == user_id).first()


def create_db_user(db: Session, user_create_schema: UserCreate) -> UserModel.User:
    """
    Creates a new user in the database and an associated account.

    Args:
        db: SQLAlchemy database session.
        user_create_schema: Pydantic schema containing user creation data.

    Returns:
        The created User model instance.
    """
    hashed_password = get_password_hash(user_create_schema.password)
    user_id = str(uuid.uuid4()) # Generate a string UUID for the user ID

    db_user = UserModel.User(
        id=user_id,
        name=user_create_schema.name,
        email=user_create_schema.email,
        password=hashed_password,
        role=UserRole.USER # Default role, can be made more flexible if needed
        # is_active, created_at, updated_at are handled by CommonModel
    )
    db.add(db_user)
    # It's often better to commit once after all related objects are added.
    # db.commit()
    # db.refresh(db_user)

    # Create an associated account for the new user
    # AccountModel uses CommonModel, so 'id' is auto-increment int.
    # user_id in AccountModel is a string foreign key to User.id.
    user_account = AccountModel(
        user_id=user_id, # Link to the User's string ID
        total_balance=Decimal("40000.00"), # Use Decimal for currency
        available_balance=Decimal("40000.00"), # Use Decimal
        year=str(datetime.now().year)
        # is_active, created_at, updated_at are handled by CommonModel
    )
    db.add(user_account)

    db.commit() # Commit both user and account together
    db.refresh(db_user)
    db.refresh(user_account) # Refresh to get DB-generated values if any (like Account.id)

    return db_user


def signup_user(db: Session, user_create_schema: UserCreate) -> UserModel.User:
    """
    Handles user signup. Checks for existing email and creates a new user.
    Raises HTTPException if email already exists.
    """
    existing_user = get_user_by_email(db, email=user_create_schema.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 409 Conflict is suitable for existing resource
            detail="Email already registered.",
        )
    new_user = create_db_user(db=db, user_create_schema=user_create_schema)
    return new_user


def authenticate_user(db: Session, user_credentials: LoginRequest) -> Optional[UserModel.User]:
    """
    Authenticates a user based on email and password.
    Returns the User model instance if authentication is successful, otherwise None.
    Note: This function does NOT create a user if not found.
    """
    member = get_user_by_email(db, email=user_credentials.email)
    if not member:
        return None # User not found
    if not verify_password(user_credentials.password, member.password):
        return None # Invalid password
    return member


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data: Dictionary containing data to encode in the token (e.g., user_id, email, role).
        expires_delta: Optional timedelta object for token expiry. Defaults to a short period.

    Returns:
        The encoded JWT access token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default expiry if not provided (e.g., from settings or a fixed short time)
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> UserModel.User: # Should return the User model instance
    """
    Dependency to get the current authenticated user from a JWT token.
    Decodes the token, validates it, and retrieves the user from the database.
    Raises HTTPException if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # TokenData schema can be used here for validation if desired, though direct dict access is also common.
        # token_payload = TokenData(**payload) # Example if using TokenData for payload validation

        user_id_from_token: str = payload.get("id") # Assuming 'id' (user's string ID) is in the token
        if user_id_from_token is None:
            # Fallback to email if 'id' is not in token (legacy tokens?)
            # This part should be consistent with what create_access_token puts in 'data'
            email_from_token: str = payload.get("email")
            if email_from_token is None:
                raise credentials_exception
            user = get_user_by_email(db, email=email_from_token)
        else:
            user = get_user_by_id(db, user_id=user_id_from_token)

        if user is None:
            raise credentials_exception
        if not user.is_active: # Check if user is active
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        return user
    except JWTError:
        raise credentials_exception


# The function `create_user_by_email` seems redundant if `create_db_user` or `signup_user` are used.
# It also doesn't hash the password. I'll comment it out for now.
# def create_user_by_email(db: Session,email: str,password:str):
#     db_user = UserModel.User(email=email, password=password,role=UserRole.USER,id=str(uuid.uuid4()))
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db.query(UserModel.User).filter(UserModel.User.email == email).first()


def read_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel.User]: # Added default values and List type hint
    """Reads all users with pagination."""
    return db.query(UserModel.User).offset(skip).limit(limit).all()
