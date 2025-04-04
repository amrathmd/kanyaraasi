# fastapi
import uuid
import asyncio
import os

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from sqlalchemy.orm import Session

from datetime import datetime


from app.api.endpoints.document.function import get_month, generate_presigned_url, create_document_inprogress, \
    update_document_status_util, get_document_by_id, get_current_month_docs, build_object_key, \
    mark_document_duplicate, get_document_details_by_gst_and_id, create_document_info

from app.api.endpoints.account.function import get_account_balance

update_document_status_util, get_document_by_id, build_object_key, \
    mark_document_duplicate
from app.api.endpoints.user import functions as user_functions
from app.core.dependencies import get_db
from app.schemas.user import MyUser,User
from app.schemas.document import GetPresignedUrl, SendPresignedUrl, GetDocuments, Document
from app.utils.constant.globals import DocumentStatus
from app.utils.ocr import process_image
from app.utils.s3_utils import upload_file_to_s3, download_file_from_s3
bucket_name = "kanyaraasi-hugohub"
document_module = APIRouter()
@document_module.post("/presigned-url",response_model= SendPresignedUrl)
async def get_presigned_url(current_user: Annotated[User, Depends(user_functions.get_current_user)],content_object : GetPresignedUrl,db: Session = Depends(get_db)) -> SendPresignedUrl:

    print(current_user)
    year = str(datetime.now().year)
    month = get_month(datetime.now().month)
    email = current_user.email
    document_id = str(uuid.uuid4())
    user_id = current_user.id

    if content_object.content_type == "image/jpeg":
        extension = "jpeg"
    elif (content_object.content_type == "image/jpg"):
        extension = "jpg"
    elif (content_object.content_type == "image/png"):
        extension = "png"
    else:
        raise Exception("invalid content type")
    path = f"{year}/{month}/{email}/{document_id}.{extension}"

    url = generate_presigned_url(bucket_name=bucket_name,object_key=path,content_type=content_object.content_type)
    create_document_inprogress(db,document_id=document_id,extension=extension,email=email,year=year,month=month,user_id=user_id)
    return SendPresignedUrl(presigned_url=url,document_code = document_id)

@document_module.post('/update-document-status/{document_id}')
def update_document_status(current_user: Annotated[User, Depends(user_functions.get_current_user)], document_id: str, db: Session = Depends(get_db)):
    update_document_status_util(db,document_id, DocumentStatus.UPLOADED)

    document = get_document_by_id(db, document_id)

    year = str(datetime.now().year)
    month = get_month(datetime.now().month)
    email = current_user.email
    extension = document.extension

    path = f"{year}/{month}/{email}/{document_id}.{extension}"

    process_ocr(path, document_id, extension,db=db)
    return {
        "status": "successfull"
    }

def process_ocr(path, document_id, extension, db: Session ):
    current_working_directory = os.getcwd()

    download_file_from_s3(path, f"{current_working_directory}/{document_id}.{extension}")

    response = asyncio.run(process_image(document_id, extension))

    print(response.get('gstin'))
    print(response.get('cgst'))
    print(response.get('sgst'))
    print(response.get('total'))

    if response.get('gstin') is None or response.get('cgst') is None or response.get('sgst') is None or response.get('total') is None:
        mark_document_duplicate(db, document_id, "Poor image quality, unable to process")
        return

    document = get_document_by_id(db, document_id)
    account_balance = get_account_balance(db, document.user_id)
    if account_balance and account_balance["available_balance"] is not None:
        available_balance = account_balance["available_balance"]
        if available_balance < response.get('total'):
            mark_document_duplicate(db, document_id, "Not enough balance")

    if get_document_details_by_gst_and_id(db, response.get('gstin'), document_id):
        mark_document_duplicate(db, document_id, "Duplicate GST number found")
    else:
        create_document_info(db, document_id, response.get('gstin'), response.get('total'), response.get('cgst'), response.get('sgst'))


@document_module.get('/get-docs')
async def get_documents_curr_month(current_user: Annotated[User, Depends(user_functions.get_current_user)],db : Session = Depends(get_db)):

    documents = get_current_month_docs(db,current_user.id)
    document_list = []
    for document in documents:
        reason = ""
        if document.reason != None:
            reason = document.reason
        object_key = build_object_key(current_user.email,document_id=document.document_id,extension = document.extension)

        url = generate_presigned_url(bucket_name=bucket_name,object_key=object_key,param_type="get_object")

        document_list.append(Document(
            document_id=document.document_id,
            status=document.status,
            year=document.year,
            month=document.month,
            reason=reason,
            url=url
        ))

    return GetDocuments(documents=document_list)
