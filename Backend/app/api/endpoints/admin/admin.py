# admin.py
# API endpoints for administrative tasks, primarily focused on document management.

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from datetime import datetime

from sqlalchemy.orm import Session

# User-related imports
from app.models.user import User as UserModel
from app.api.endpoints.user import functions as user_crud_functions

# Document-related imports
from app.schemas.document import (
    DocumentResponse, DocumentListResponse,
    DocumentDetailResponse, DocumentDetailListResponse,
    DocumentStatusUpdate # Using the refactored schema for status updates
)
from app.api.endpoints.document import functions as doc_functions

# Account-related imports (assuming these functions exist and are refactored)
from app.api.endpoints.account import functions as account_functions

from app.core.dependencies import get_db
from app.core.settings import S3_BUCKET_NAME # For presigned URLs
from app.utils.constant.globals import UserRole, DocumentStatus


admin_module = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={
        401: {"description": "User not authorized"},
        403: {"description": "Operation not permitted"},
        404: {"description": "Resource not found"}
    }
)

def _ensure_admin_role(current_user: UserModel):
    """Helper to check if the current user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # More appropriate than 401 if authenticated but not authorized
            detail="User does not have admin privileges."
        )

@admin_module.get(
    '/documents/uploaded',
    response_model=DocumentListResponse,
    summary="Get All Uploaded Documents (Current Month)",
    description="Retrieves all documents with 'UPLOADED' status for the current month. Admin only."
)
async def get_all_uploaded_documents_current_month(
    current_user: Annotated[UserModel, Depends(user_crud_functions.get_current_user)],
    db: Session = Depends(get_db)
) -> DocumentListResponse:
    _ensure_admin_role(current_user)

    now = datetime.now()
    year = str(now.year)
    month_name = doc_functions.get_month_name(now.month) # Use refactored function

    document_models = doc_functions.get_all_documents_for_period_and_status(
        db, year=year, month=month_name, status=DocumentStatus.UPLOADED
    )

    document_responses: List[DocumentResponse] = []
    for doc_model in document_models:
        doc_resp = DocumentResponse.from_orm(doc_model)
        # Generate download URL if needed for admin view
        s3_object_key = doc_functions.build_s3_object_key(
            user_email=doc_model.email, # Assuming email snapshot is on doc_model
            year=doc_model.year,
            month=doc_model.month,
            doc_id=doc_model.document_id, # business_id
            extension=doc_model.extension
        )
        doc_resp.url_for_download = doc_functions.generate_s3_presigned_url(
            bucket_name=S3_BUCKET_NAME,
            object_key=s3_object_key,
            param_type="get_object"
        )
        document_responses.append(doc_resp)

    return DocumentListResponse(documents=document_responses)


@admin_module.get(
    '/documents/approved',
    response_model=DocumentDetailListResponse, # Returns detailed list
    summary="Get All Approved Documents (Current Month)",
    description="Retrieves all documents with 'APPROVED' status for the current month, including their extracted info. Admin only."
)
async def get_all_approved_documents_current_month(
    current_user: Annotated[UserModel, Depends(user_crud_functions.get_current_user)],
    db: Session = Depends(get_db)
) -> DocumentDetailListResponse:
    _ensure_admin_role(current_user)

    now = datetime.now()
    year = str(now.year)
    month_name = doc_functions.get_month_name(now.month)

    document_models = doc_functions.get_all_documents_for_period_and_status(
        db, year=year, month=month_name, status=DocumentStatus.APPROVED
    )

    detailed_responses: List[DocumentDetailResponse] = []
    for doc_model in document_models:
        doc_info_model = doc_functions.get_document_info_by_parent_doc_pk(db, parent_document_pk=doc_model.id)

        doc_detail_resp = DocumentDetailResponse.from_orm(doc_model)
        if doc_info_model:
            doc_detail_resp.gst_in = doc_info_model.gst_in
            doc_detail_resp.total_amount = doc_info_model.total_amount
            doc_detail_resp.cgst_percent = doc_info_model.cgst_percent
            doc_detail_resp.sgst_percent = doc_info_model.sgst_percent

        # Optionally add download URL for admin
        s3_object_key = doc_functions.build_s3_object_key(
             user_email=doc_model.email, year=doc_model.year, month=doc_model.month,
             doc_id=doc_model.document_id, extension=doc_model.extension
        )
        doc_detail_resp.url_for_download = doc_functions.generate_s3_presigned_url(
            bucket_name=S3_BUCKET_NAME, object_key=s3_object_key, param_type="get_object"
        )
        detailed_responses.append(doc_detail_resp)

    return DocumentDetailListResponse(documents=detailed_responses)


@admin_module.get(
    '/documents/{document_business_id}/details',
    response_model=DocumentDetailResponse,
    summary="Get Specific Document Details (Admin)",
    description="Retrieves detailed information for a specific document by its business ID. Admin only."
)
async def get_specific_document_details(
    document_business_id: str,
    current_user: Annotated[UserModel, Depends(user_crud_functions.get_current_user)],
    db: Session = Depends(get_db)
) -> DocumentDetailResponse:
    _ensure_admin_role(current_user)

    doc_model = doc_functions.get_document_by_business_id(db, business_id=document_business_id)
    if not doc_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    doc_info_model = doc_functions.get_document_info_by_parent_doc_pk(db, parent_document_pk=doc_model.id)

    doc_detail_resp = DocumentDetailResponse.from_orm(doc_model)
    if doc_info_model: # Populate fields from DocumentInfo
        doc_detail_resp.gst_in = doc_info_model.gst_in
        doc_detail_resp.total_amount = doc_info_model.total_amount
        doc_detail_resp.cgst_percent = doc_info_model.cgst_percent
        doc_detail_resp.sgst_percent = doc_info_model.sgst_percent

    # Optionally add download URL
    s3_object_key = doc_functions.build_s3_object_key(
         user_email=doc_model.email, year=doc_model.year, month=doc_model.month,
         doc_id=doc_model.document_id, extension=doc_model.extension
    )
    doc_detail_resp.url_for_download = doc_functions.generate_s3_presigned_url(
        bucket_name=S3_BUCKET_NAME, object_key=s3_object_key, param_type="get_object"
    )
    return doc_detail_resp


@admin_module.put( # Changed to PUT for idempotent status update
    '/documents/{document_business_id}/status',
    response_model=DocumentResponse, # Return the updated document
    summary="Update Document Status (Admin)",
    description="Allows an admin to manually approve or reject a document and provide a reason."
)
async def admin_update_document_status(
    document_business_id: str,
    status_update_payload: DocumentStatusUpdate, # Request body with new status and reason
    current_user: Annotated[UserModel, Depends(user_crud_functions.get_current_user)],
    db: Session = Depends(get_db)
) -> DocumentResponse:
    _ensure_admin_role(current_user)

    # The DocumentStatusUpdate schema uses 'document_id' for the business ID.
    # Here, we take it from path, so payload 'document_id' is ignored or should match path.
    # For simplicity, we assume status_update_payload only contains 'status' and 'reason'.

    doc_model = doc_functions.get_document_by_business_id(db, business_id=document_business_id)
    if not doc_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found for status update.")

    # Prevent updating status if document is not in a state that allows manual admin change (e.g., already processed by OCR)
    # This logic might need adjustment based on exact workflow.
    if doc_model.status not in [DocumentStatus.UPLOADED, DocumentStatus.PENDING_REVIEW]: # Example valid previous statuses
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document status '{doc_model.status.name}' cannot be manually changed by admin at this stage."
        )

    if status_update_payload.status == DocumentStatus.APPROVED:
        # If approving, check balance (similar to OCR logic but initiated by admin)
        doc_info = doc_functions.get_document_info_by_parent_doc_pk(db, parent_document_pk=doc_model.id)
        if not doc_info or not doc_info.total_amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document info with total amount not found. Cannot approve.")

        # Assuming account_functions.get_available_balance_for_user and update_user_account_balance exist and are refactored
        available_balance = account_functions.get_available_balance_for_user(db, user_id=doc_model.user_id)

        if available_balance is None or available_balance < doc_info.total_amount:
            # Even if admin approves, if balance is insufficient, it should be flagged or handled.
            # For now, let's reject it or require admin to override.
            # Or, simply record admin approval but note the balance issue.
            # Here, we block approval if balance is insufficient.
            updated_doc = doc_functions.update_document_status_and_reason(
                db, doc_business_id, DocumentStatus.REJECTED,
                status_update_payload.reason or "Admin approved but insufficient balance."
            )
            if not updated_doc: # Should not happen if doc_model was found
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update document status after balance check.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance to approve bill. Bill amount: {doc_info.total_amount}, Available: {available_balance}. Document marked as REJECTED."
            )
        else:
            # Deduct balance
            account_functions.update_user_account_balance(
                db, user_id=doc_model.user_id, year=doc_model.year, charge_amount=doc_info.total_amount
            )
            updated_doc = doc_functions.update_document_status_and_reason(
                db, doc_business_id, DocumentStatus.APPROVED, status_update_payload.reason
            )
    elif status_update_payload.status == DocumentStatus.REJECTED:
        updated_doc = doc_functions.update_document_status_and_reason(
            db, doc_business_id, DocumentStatus.REJECTED, status_update_payload.reason
        )
    else:
        # Admin might be setting other statuses like PENDING_REVIEW etc.
        updated_doc = doc_functions.update_document_status_and_reason(
            db, doc_business_id, status_update_payload.status, status_update_payload.reason
        )

    if not updated_doc: # Should ideally not happen if doc_model was found initially
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update document status.")

    return DocumentResponse.from_orm(updated_doc)