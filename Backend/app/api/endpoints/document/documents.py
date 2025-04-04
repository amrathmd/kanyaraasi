# fastapi
from fastapi import APIRouter, Depends, HTTPException

# sqlalchemy
from sqlalchemy.orm import Session

# import
from app.core.dependencies import get_db, oauth2_scheme
from app.schemas.user import User, UserCreate, UserUpdate, DocumentRequest
from app.api.endpoints.user import functions as user_functions
from app.utils.s3_utils import download_file_from_s3, upload_file_to_s3

document_module = APIRouter()


# @user_module.get('/')
# async def read_auth_page():
#     return {"msg": "Auth page Initialization done"}


