# fastapi
import uuid
import asyncio

from fastapi import APIRouter, Depends, HTTPException,status
from typing import Annotated

from sqlalchemy.orm import Session

from app.api.endpoints.account.function import get_account_balance, update_account_balance
from app.schemas.document import UpdateDocStatus, DocumentDetails, DocumentDetailsList

from datetime import datetime


from app.api.endpoints.document.function import get_month, generate_presigned_url, create_document_inprogress, \
    update_document_status_util, get_document_by_id, get_current_month_docs, build_object_key, \
    get_current_month_all_user_docs, get_document_info_by_id
from app.api.endpoints.user import functions as user_functions
from app.core.dependencies import get_db
from app.schemas.user import MyUser,User
from app.schemas.document import GetPresignedUrl, SendPresignedUrl, GetDocuments, Document, UpdateDocStatus
from app.utils.constant.globals import UserRole, DocumentStatus
from app.utils.ocr import process_image
from app.utils.s3_utils import upload_file_to_s3, download_file_from_s3
bucket_name = "kanyaraasi-hugohub"
admin_module = APIRouter()

@admin_module.get('/get-all-docs')
async def get_all_documents_curr_month(current_user: Annotated[User, Depends(user_functions.get_current_user)],db : Session = Depends(get_db)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized"
        )
    documents = get_current_month_all_user_docs(db, DocumentStatus.UPLOADED)
    document_list = []
    for document in documents:
        reason = ""
        if document.reason != None:
            reason = document.reason
        object_key = build_object_key(document.email,document_id=document.document_id,extension = document.extension)

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

@admin_module.get('/get-approved-docs')
async def get_approved_documents_curr_month(current_user: Annotated[User, Depends(user_functions.get_current_user)],db : Session = Depends(get_db)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized"
        )
    documents = get_current_month_all_user_docs(db, DocumentStatus.APPROVED)
    document_list = []
    for document in documents:
        document_info_obj = get_document_info_by_id(db, document.document_id)

        document_list.append(DocumentDetails(
            document_id=document.document_id,
            status=document.status,
            email=document.email,
            year=document.year,
            month=document.month,
            gst_number=document_info_obj.gst_in,
            total_amount=document_info_obj.total_amount,
            cgst_percent=document_info_obj.cgst_percent,
            sgst_percent=document_info_obj.sgst_percent
        ))

    return DocumentDetailsList(documents=document_list)

@admin_module.get('/get-document-details/{document_id}')
async def get_approved_documents_curr_month(current_user: Annotated[User, Depends(user_functions.get_current_user)],document_id:str,db : Session = Depends(get_db)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized"
        )

    document = get_document_by_id(db, document_id)
    document_info_obj = get_document_info_by_id(db, document_id)

    return DocumentDetails(
        document_id=document.document_id,
        status=document.status,
        email=document.email,
        year=document.year,
        month=document.month,
        gst_number=document_info_obj.gst_in,
        total_amount=document_info_obj.total_amount,
        cgst_percent=document_info_obj.cgst_percent,
        sgst_percent=document_info_obj.sgst_percent
    )

@admin_module.post('/update-status')
async def update_document_status(updateDocStatus : UpdateDocStatus, current_user: Annotated[User, Depends(user_functions.get_current_user)],db : Session = Depends(get_db)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized"
        )

    document_details = get_document_by_id(db, updateDocStatus.document_id)
    if document_details.status != DocumentStatus.UPLOADED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    if updateDocStatus.status == DocumentStatus.REJECTED:
        update_document_status_util(db, updateDocStatus.document_id, updateDocStatus.status)
        return {
            "status" : "update success"
        }
    document_info = get_document_info_by_id(db, updateDocStatus.document_id)

    if document_info != None and document_details != None:
        account_balance = get_account_balance(db, document_details.user_id)
        if account_balance:
            available_balance = account_balance["available_balance"]
            if available_balance < document_info.total_amount:
                update_document_status_util(db, updateDocStatus.document_id, DocumentStatus.REJECTED)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Not enough balance to approve bill"
                )
            else :
                update_account_balance(document_details.user_id, available_balance, document_info.total_amount, document_details.year, db)
                update_document_status_util(db, updateDocStatus.document_id, DocumentStatus.APPROVED)
                return {
                    "status" : "update_success"
                }

        else :
            update_document_status_util(db, updateDocStatus.document_id, DocumentStatus.REJECTED)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="account details not exist"
            )
    else :
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no such document found"
        )