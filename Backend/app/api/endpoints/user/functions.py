from fastapi import HTTPException, status, Depends
from typing import Annotated
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

# from auth import models, schemas
from passlib.context import CryptContext
from jose import JWTError, jwt
import uuid

# import 
from app.models import user as UserModel
from app.schemas.user import MyUser,Token
from app.core.settings import SECRET_KEY, REFRESH_SECRET_KEY, ALGORITHM
from app.core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.dependencies import get_db, oauth2_scheme
from app.utils.constant.globals import UserRole
from app.models.account import Account

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# get user by email 
def get_user_by_email(db: Session, email: str):
    return db.query(UserModel.User).filter(UserModel.User.email == email).first()

#create user by email
def create_user_by_email(db: Session,email: str,password:str):
    db_user = UserModel.User(email=email, password=password,role=UserRole.USER,id=str(uuid.uuid4()))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db.query(UserModel.User).filter(UserModel.User.email == email).first()
# get user by id
def get_user_by_id(db: Session, user_id: int):
    db_user = db.query(UserModel.User).filter(UserModel.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# crete new user 
def create_new_user(db: Session, user: MyUser):
    hashed_password = pwd_context.hash(user.password)
    id = str(uuid.uuid4())
    new_user = UserModel.User(name=user.name, email=user.email, password=hashed_password, role= UserRole.USER, id = id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    user_account = Account(
        user_id = id,
        total_balance = 40000.0,
        available_balance = 40000.0,
        year = str(datetime.now().year)
    )
    db.add(user_account)
    db.commit()
    db.refresh(user_account)
    return new_user


# get all user 
def read_all_user(db: Session, skip: int, limit: int):
    return db.query(UserModel.User).offset(skip).limit(limit).all()

# =====================> login/logout <============================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def signup_user(db: Session, user: MyUser):
    member = get_user_by_email(db, user.email)
    if member:
        return False
    create_new_user(db, user)
    return True

def authenticate_user(db: Session, user: MyUser):
    member = get_user_by_email(db, user.email)
    if not member:
        member= create_new_user(db,user)
        return member
    if not verify_password(user.password, member.password):
        return False
    return member

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# get current users info 
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print(f"Payload =====> {payload}")
        current_email: str = payload.get("email")
        if current_email is None:
            raise credentials_exception
        user = get_user_by_email(db, current_email)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

