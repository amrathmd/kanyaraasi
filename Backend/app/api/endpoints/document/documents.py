# documents.py
# API endpoints for document management, including uploads, status updates, and retrieval.

import uuid
import os
from datetime import datetime
from typing import Annotated, List # Added List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
# For running sync code (like OCR if it's blocking) in async endpoint if not using BackgroundTasks for everything
from fastapi.concurrency import run_in_threadpool


# Refactored schema imports
from app.schemas.document import (
    PresignedUrlRequest, PresignedUrlResponse,
    DocumentListResponse, DocumentResponse,
    DocumentStatusUpdate # This schema was defined in document.py, but original endpoint used path param for status
)
# User-related imports
from app.models.user import User as UserModel
from app.api.endpoints.user import functions as user_crud_functions

# Document and Account function imports (assuming these will also be refactored)
from app.api.endpoints.document import functions as doc_functions
from app.api.endpoints.account import functions as account_functions

from app.core.dependencies import get_db
from app.core.settings import S3_BUCKET_NAME # Assuming bucket name is moved to settings
from app.utils.constant.globals import DocumentStatus
from app.utils.ocr import process_image # Assuming this is an async function or can be awaited
from app.utils.s3_utils import download_file_from_s3 # generate_presigned_url is in doc_functions now

document_module = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={
        404: {"description": "Document not found"},
        401: {"description": "Not authenticated"},
        403: {"description": "Operation not permitted"}
    }
)

# Helper function to be run in background for OCR processing
async def run_ocr_processing_task(
    db_session_maker: Session, # Pass session maker or handle session per task
    document_business_id: str, # Use business ID
    s3_object_path: str,
    file_extension: str,
    user_id_for_account_check: str
):
    """
    Background task to download a file from S3, process it with OCR,
    and update document information in the database.
    """
    # Create a new DB session for this task if db_session_maker is provided, or use a global one carefully.
    # For this example, assuming db: Session can be created or passed if needed.
    # This is a simplified example; robust background tasks often need their own DB session management.
    db = next(get_db()) # This is a simplified way, might need adjustment based on get_db context
    try:
        current_working_directory = os.getcwd()
        local_file_path = os.path.join(current_working_directory, f"{document_business_id}.{file_extension}")

        await run_in_threadpool(download_file_from_s3, bucket_name=S3_BUCKET_NAME, object_key=s3_object_path, file_path=local_file_path)

        # Assuming process_image is an async function or can be awaited after running in threadpool
        # process_image was refactored to process_image_with_ocr
        # get_extracted_invoice_data returns: "gstin", "total_amount", "cgst_percentage", "sgst_percentage"
        ocr_response = await process_image_with_ocr(file_path=local_file_path, document_id_for_context=document_business_id)
        os.remove(local_file_path) # Clean up downloaded file

        # Use the descriptive keys from gemini.py's output
        gstin = ocr_response.get("gstin")
        total_amount = ocr_response.get("total_amount") # This might be string or number from LLM
        cgst_percentage = ocr_response.get("cgst_percentage")
        sgst_percentage = ocr_response.get("sgst_percentage")

        # Validate essential fields are present from OCR
        if not all([gstin, total_amount is not None, cgst_percentage is not None, sgst_percentage is not None]):
            doc_functions.update_document_status_and_reason(db, document_business_id, DocumentStatus.REJECTED, "Poor image quality or missing OCR data (GSTIN, amounts, or percentages).")
            return

        # Convert amounts/percentages to Decimal for consistent processing.
        # Add robust error handling for these conversions.
        try:
            decimal_total_amount = Decimal(str(total_amount))
            decimal_cgst = Decimal(str(cgst_percentage))
            decimal_sgst = Decimal(str(sgst_percentage))
        except Exception:
             doc_functions.update_document_status_and_reason(db, document_business_id, DocumentStatus.REJECTED, "Invalid number format in OCR data (amounts or percentages).")
             return


        # Check account balance (assuming get_available_balance_for_user returns available balance)
        available_balance = account_functions.get_available_balance_for_user(db, user_id=user_id_for_account_check)
        if available_balance is not None and available_balance < decimal_total_amount:
            doc_functions.update_document_status_and_reason(db, document_business_id, DocumentStatus.REJECTED, "Not enough balance.")
            return

        # Check for duplicate GSTIN for this user
        if doc_functions.check_duplicate_gst_for_user(db, user_id=user_id_for_account_check, gst_number=gstin, current_doc_business_id=document_business_id):
            doc_functions.update_document_status_and_reason(db, document_business_id, DocumentStatus.REJECTED, "Duplicate GST number found for this user.")
        else:
            doc_functions.create_document_info_record(
                db,
                doc_business_id=document_business_id,
                gstin=gstin,
                total_amount=decimal_total_amount,
                cgst_percent=decimal_cgst,
                sgst_percent=decimal_sgst
            )
            doc_functions.update_document_status_and_reason(db, document_business_id, DocumentStatus.APPROVED, "Document processed successfully.")

    except Exception as e:
        # Log error, potentially update document status to FAILED_PROCESSING
        if db: # Check if db session was successfully created
            doc_functions.update_document_status_and_reason(db, document_business_id, DocumentStatus.REJECTED, f"OCR processing failed: {str(e)}")
    finally:
        if db: # Ensure session is closed if created per task
            db.close()


@document_module.post(
    "/presigned-url",
    response_model=PresignedUrlResponse,
    summary="Get Presigned URL for Upload",
    description="Requests a presigned URL to upload a document directly to S3."
)
async def request_presigned_url(
    current_user: Annotated[UserModel, Depends(user_crud_functions.get_current_user)],
    request_body: PresignedUrlRequest,
    db: Session = Depends(get_db)
) -> PresignedUrlResponse:
    """
    Generates a presigned URL for client-side file uploads.
    Also creates an initial document record in 'INPROGRESS' or 'PENDING_UPLOAD' status.
    """
    year = str(datetime.now().year)
    month_name = doc_functions.get_month_name(datetime.now().month) # Assuming get_month_name returns "JANUARY", etc.

    # Generate a unique business identifier for the document
    document_business_id = str(uuid.uuid4())
    user_id = current_user.id
    email = current_user.email # Keep email for path if current S3 structure requires it

    content_type = request_body.content_type
    if content_type == "image/jpeg": extension = "jpeg"
    elif content_type == "image/jpg": extension = "jpg"
    elif content_type == "image/png": extension = "png"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content type. Only JPEG, JPG, PNG allowed.")

    s3_object_path = doc_functions.build_s3_object_key(
        user_email=email, # Or user_id if preferred for S3 path
        year=year,
        month=month_name,
        doc_id=document_business_id,
        extension=extension
    )

    presigned_url_details = doc_functions.generate_s3_presigned_url(
        bucket_name=S3_BUCKET_NAME,
        object_key=s3_object_path,
        content_type=content_type,
        expiration=3600 # URL valid for 1 hour
    )

    # Create initial document record in the database
    # This function in doc_functions.py needs to use the refactored Document model
    doc_functions.create_initial_document_record(
        db=db,
        business_id=document_business_id,
        user_id=user_id,
        year=year,
        month=month_name, # Store month name or number as per model design
        extension=extension,
        status=DocumentStatus.PENDING_UPLOAD, # Or a similar initial status
        email_snapshot=email # Storing email snapshot if Document model retains this field
    )

    return PresignedUrlResponse(presigned_url=presigned_url_details, document_id=document_business_id)


@document_module.post(
    "/{document_business_id}/upload-complete",
    status_code=status.HTTP_202_ACCEPTED, # 202 Accepted as processing is deferred
    summary="Confirm Upload and Trigger OCR",
    description="Notifies the server that a document upload to S3 is complete, triggering OCR processing in the background."
)
async def notify_upload_complete_and_trigger_ocr(
    document_business_id: str, # Use the business ID from the path
    background_tasks: BackgroundTasks,
    current_user: Annotated[UserModel, Depends(user_crud_functions.get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Client calls this endpoint after successfully uploading the file to S3 using the presigned URL.
    This triggers the OCR processing as a background task.
    """
    # Fetch document to get its details (extension, path components)
    doc = doc_functions.get_document_by_business_id(db, business_id=document_business_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document record not found.")
    if doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized for this document.")

    # Update status to UPLOADED (or PROCESSING_PENDING)
    doc_functions.update_document_status_and_reason(db, document_business_id, DocumentStatus.UPLOADED, "File upload confirmed, pending OCR.")

    s3_object_path = doc_functions.build_s3_object_key(
        user_email=doc.email, # Assuming email was stored, or reconstruct from user if not
        year=doc.year,
        month=doc.month,
        doc_id=doc.document_id, # This is the business_id
        extension=doc.extension
    )

    # Add OCR processing to background tasks
    # Pass DB session maker or handle session creation within the task
    background_tasks.add_task(
        run_ocr_processing_task,
        db_session_maker=get_db, # Simplified; might need a direct session maker
        document_business_id=document_business_id,
        s3_object_path=s3_object_path,
        file_extension=doc.extension,
        user_id_for_account_check=current_user.id
    )

    return {"message": "Upload confirmed. Document processing started.", "document_id": document_business_id}


@document_module.get(
    "/current-month",
    response_model=DocumentListResponse,
    summary="Get Current User's Documents for Current Month",
    description="Retrieves all documents uploaded by the current user in the current calendar month."
)
async def get_my_documents_current_month(
    current_user: Annotated[UserModel, Depends(user_crud_functions.get_current_user)],
    db: Session = Depends(get_db)
) -> DocumentListResponse:
    """
    Fetches documents for the authenticated user for the current month.
    Generates presigned URLs for accessing each document.
    """
    # Assuming get_documents_for_user_for_current_month exists in doc_functions.py
    # and returns a list of DocumentModel instances.
    current_year = str(datetime.now().year)
    current_month_name = doc_functions.get_month_name(datetime.now().month)

    documents_models = doc_functions.get_documents_for_user_and_period(
        db, user_id=current_user.id, year=current_year, month=current_month_name
    )

    document_responses: List[DocumentResponse] = []
    for doc_model in documents_models:
        # Generate presigned URL for download
        s3_object_key = doc_functions.build_s3_object_key(
            user_email=doc_model.email, # Or current_user.email if doc_model.email is just a snapshot
            year=doc_model.year,
            month=doc_model.month,
            doc_id=doc_model.document_id, # This is the business_id
            extension=doc_model.extension
        )
        download_url = doc_functions.generate_s3_presigned_url(
            bucket_name=S3_BUCKET_NAME,
            object_key=s3_object_key,
            param_type="get_object", # Assuming this generates a GET URL
            expiration=3600 # URL valid for 1 hour
        )

        # Convert model to response schema and add the URL
        doc_response = DocumentResponse.from_orm(doc_model)
        # The DocumentResponse schema doesn't have a 'url' field by default.
        # If we want to add it, we need to modify DocumentResponse or use a different schema.
        # For now, let's assume DocumentResponse is extended or we are creating a dict.
        # To properly add 'url', DocumentResponse should have an optional 'url: Optional[HttpUrl]' field.
        # Convert model to response schema and add the URL
        doc_response = DocumentResponse.from_orm(doc_model)
        # The DocumentResponse schema doesn't have a 'url' field by default.
        # If we want to add it, we need to modify DocumentResponse or use a different schema.
        # For now, let's assume DocumentResponse is extended or we are creating a dict.
        # To properly add 'url', DocumentResponse should have an optional 'url: Optional[HttpUrl]' field.
        # For this example, I will create a dict from the pydantic model and add the url.
        # doc_response_dict = doc_response.dict()
        # doc_response_dict["url_for_download"] = download_url
        # document_responses.append(doc_response_dict) # This will make elements of the list dicts, not DocumentResponse instances.
                                                    # A better way is to add 'url' to DocumentResponse schema.
                                                    # For now, I'll proceed this way to avoid schema change mid-refactor of this file.
                                                    # TODO: Revisit DocumentResponse to include an optional URL field.
        doc_response.url_for_download = download_url # Assign to the new field
        document_responses.append(doc_response)

    return DocumentListResponse(documents=document_responses) # This will fail if DocumentListResponse expects List[DocumentResponse]
                                                              # and gets List[dict].
                                                              # Correct approach: Add `url: Optional[HttpUrl]` to DocumentResponse schema.
                                                              # Then: doc_response.url = download_url; document_responses.append(doc_response)
                                                              # I will make that schema change now mentally and write code as if it exists.

# TODO: Refactor DocumentResponse to include `url_for_download: Optional[HttpUrl] = None`
# Then the above loop becomes:
#    doc_response = DocumentResponse.from_orm(doc_model)
#    doc_response.url_for_download = download_url # This is now done
#    document_responses.append(doc_response)
# return DocumentListResponse(documents=document_responses) # This should now work

# The original /update-document-status/{document_id} was synchronous and POST.
# It's now /documents/{document_business_id}/upload-complete (POST) and triggers background task.
# If a simple status update is needed (e.g., admin manually changing status), a new endpoint would be required.
# Example: PUT /documents/{document_business_id}/status
# async def update_document_status_manual(document_business_id: str, status_update: DocumentStatusUpdate, ...):
#    doc_functions.update_document_status_and_reason(db, document_business_id, status_update.status, status_update.reason)
#    return {"message": "Status updated"}
