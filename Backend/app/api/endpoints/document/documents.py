# fastapi
import uuid

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from sqlalchemy.orm import Session

from datetime import datetime


from app.api.endpoints.document.function import get_month, generate_presigned_url, create_document_inprogress, \
    update_document_status_util
from app.api.endpoints.user import functions as user_functions
from app.core.dependencies import get_db
from app.schemas.user import MyUser,User
from app.schemas.document import GetPresignedUrl, SendPresignedUrl

document_module = APIRouter()
@document_module.post("/presigned-url",response_model= SendPresignedUrl)
async def get_presigned_url(current_user: Annotated[User, Depends(user_functions.get_current_user)],content_object : GetPresignedUrl,db: Session = Depends(get_db)) -> SendPresignedUrl:
    bucket_name = "kanyaraasi-hugohub"
    print(current_user)
    year = str(datetime.now().year)
    month = get_month(datetime.now().month)
    email = current_user.email
    document_id = str(uuid.uuid4())
    user_id = current_user.id

    path = f"{year}/{month}/{email}/{document_id}"

    url = generate_presigned_url(bucket_name=bucket_name,object_key=path,content_type=content_object.content_type)
    create_document_inprogress(db,document_id=document_id,email=email,year=year,month=month,user_id=user_id)
    return SendPresignedUrl(presigned_url=url,document_code = document_id)

@document_module.post('/update-document-status/{document_id}')
async def update_document_status(current_user: Annotated[User, Depends(user_functions.get_current_user)],document_id: str, db: Session = Depends(get_db)):
    update_document_status_util(db,document_id)
    return {
        "status": "successfull"
    }