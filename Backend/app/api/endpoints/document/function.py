# function.py for documents
# Contains helper and business logic functions for document-related operations.

import logging
from datetime import datetime
from typing import List, Optional
from decimal import Decimal # For handling currency values

import boto3
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session
from sqlalchemy import extract # For date part extraction

# Model imports using explicit aliases
from app.models.document import Document as DocumentModel
from app.models.document_info import DocumentInfo as DocumentInfoModel

# Settings and constants
from app.core.settings import AWS_S3_REGION_NAME, S3_BUCKET_NAME # Expect these in settings
from app.utils.constant.globals import DocumentStatus

# Setup logger
logger = logging.getLogger(__name__)

_MONTH_NAMES = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

def get_month_name(month_number: int) -> str:
    """Converts a month number (1-12) to its name."""
    if 1 <= month_number <= 12:
        return _MONTH_NAMES[month_number - 1]
    raise ValueError("Month number must be between 1 and 12.")


def generate_s3_presigned_url(
    bucket_name: str,
    object_key: str,
    content_type: Optional[str] = None, # Optional for get_object
    param_type: str = "put_object", # "put_object" or "get_object"
    expiration_seconds: int = 3600,
) -> Optional[str]:
    """
    Generates a presigned URL for S3 objects (either for uploading or downloading).
    """
    s3_client = boto3.client("s3", region_name=AWS_S3_REGION_NAME)
    try:
        params = {"Bucket": bucket_name, "Key": object_key}
        if param_type == "put_object":
            if not content_type:
                raise ValueError("content_type is required for put_object presigned URL.")
            params["ContentType"] = content_type

        url = s3_client.generate_presigned_url(
            ClientMethod=param_type,
            Params=params,
            ExpiresIn=expiration_seconds
        )
        logger.info(f"Generated presigned URL for s3://{bucket_name}/{object_key}): {url}")
        return url
    except ClientError as e:
        logger.error(f"Error generating presigned URL for {object_key}: {e}")
        return None
    except ValueError as e:
        logger.error(f"ValueError in generating presigned URL: {e}")
        return None


def create_initial_document_record(
    db: Session,
    business_id: str, # This is Document.document_id (the string business identifier)
    user_id: str,     # This is User.id (the string user identifier)
    year: str,
    month: str, # Expecting month name like "January"
    extension: str,
    status: DocumentStatus,
    email_snapshot: Optional[str] = None # If Document model still stores this
) -> DocumentModel:
    """
    Creates an initial record for a document in the database.
    Uses the refactored DocumentModel which includes CommonModel fields.
    """
    document = DocumentModel(
        document_id=business_id, # This is the unique business ID (string)
        user_id=user_id,
        year=year,
        month=month, # Ensure this aligns with how month is stored (e.g., "January" or "01")
        extension=extension,
        status=status,
        email=email_snapshot # If the model has this field
        # id (PK), is_active, created_at, updated_at are handled by CommonModel
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    logger.info(f"Created initial document record with business_id: {business_id}, DB PK id: {document.id}")
    return document


def update_document_status_and_reason(
    db: Session,
    doc_business_id: str, # Use business_id to fetch
    new_status: DocumentStatus,
    reason: Optional[str] = None
) -> Optional[DocumentModel]:
    """
    Updates the status and optionally the reason for a document.
    Fetches document by its string business_id.
    """
    document = db.query(DocumentModel).filter(DocumentModel.document_id == doc_business_id).first()
    if document:
        document.status = new_status
        if reason is not None: # Only update reason if provided
            document.reason = reason
        document.updated_at = datetime.utcnow() # Manually update if not auto-updating in all cases via CommonModel
        db.commit()
        db.refresh(document)
        logger.info(f"Updated document {doc_business_id} to status {new_status.name} with reason: {reason or 'N/A'}")
        return document
    logger.warning(f"Document with business_id {doc_business_id} not found for status update.")
    return None


def get_document_by_business_id(db: Session, business_id: str) -> Optional[DocumentModel]:
    """Retrieves a document by its string business_id."""
    return db.query(DocumentModel).filter(DocumentModel.document_id == business_id).first()


def get_documents_for_user_and_period(
    db: Session,
    user_id: str,
    year: str,
    month: str # Expecting month name like "January"
) -> List[DocumentModel]:
    """
    Retrieves documents for a specific user, year, and month.
    """
    # Ensure month comparison is correct based on how it's stored in DB.
    # If storing month names, direct comparison is fine.
    documents = db.query(DocumentModel).filter(
        DocumentModel.user_id == user_id,
        DocumentModel.year == year,
        DocumentModel.month == month,
        DocumentModel.is_active == True # Typically only fetch active documents
        # DocumentModel.status != DocumentStatus.INPROGRESS # Or other status filters
    ).order_by(DocumentModel.created_at.desc()).all()
    return documents


def get_all_documents_for_period_and_status(
    db: Session,
    year: str,
    month: str, # Expecting month name
    status: Optional[DocumentStatus] = None
) -> List[DocumentModel]:
    """
    Retrieves all documents for a given year, month, and optionally status.
    Used for admin purposes or system processing.
    """
    query = db.query(DocumentModel).filter(
        DocumentModel.year == year,
        DocumentModel.month == month,
        DocumentModel.is_active == True
    )
    if status:
        query = query.filter(DocumentModel.status == status)
    return query.order_by(DocumentModel.created_at.desc()).all()


def build_s3_object_key(user_email: str, year: str, month: str, doc_id: str, extension: str) -> str:
    """Constructs the S3 object key."""
    # Path construction should be consistent with how it was originally designed.
    # Example: "2023/January/user@example.com/doc_uuid.pdf"
    return f"{year}/{month}/{user_email}/{doc_id}.{extension}"


def check_duplicate_gst_for_user(
    db: Session,
    user_id: str, # Check for this user
    gst_number: str,
    current_doc_business_id: Optional[str] = None # Exclude current document if updating
) -> bool:
    """
    Checks if a document with the same GSTIN already exists for the given user,
    excluding the current document if its business_id is provided.
    """
    query = db.query(DocumentInfoModel).join(DocumentModel, DocumentModel.id == DocumentInfoModel.document_fk_id).filter(
        DocumentModel.user_id == user_id,
        DocumentInfoModel.gst_in == gst_number,
        DocumentModel.is_active == True # Consider only active/approved duplicates?
    )
    if current_doc_business_id:
        # Exclude the current document from the check
        query = query.filter(DocumentModel.document_id != current_doc_business_id)

    existing_doc_info = query.first()
    return existing_doc_info is not None


def create_document_info_record(
    db: Session,
    doc_business_id: str, # Business ID of the parent Document
    gstin: str,
    total_amount: Decimal,
    cgst_percent: Decimal,
    sgst_percent: Decimal
) -> Optional[DocumentInfoModel]:
    """
    Creates a DocumentInfo record associated with a Document.
    The DocumentInfo model has its own integer PK (from CommonModel) and
    a document_fk_id linking to Document.id (Integer PK).
    """
    parent_document = get_document_by_business_id(db, business_id=doc_business_id)
    if not parent_document:
        logger.error(f"Cannot create DocumentInfo: Parent Document with business_id {doc_business_id} not found.")
        return None

    # Check if DocumentInfo already exists for this parent document's PK
    existing_info = db.query(DocumentInfoModel).filter(DocumentInfoModel.document_fk_id == parent_document.id).first()
    if existing_info:
        logger.warning(f"DocumentInfo record already exists for document PK {parent_document.id} (business_id {doc_business_id}). Skipping creation.")
        # Optionally, update existing_info here if that's the desired behavior
        return existing_info

    doc_info = DocumentInfoModel(
        document_fk_id=parent_document.id, # Link to the Integer PK of the Document
        gst_in=gstin,
        total_amount=total_amount, # Expecting Decimal
        cgst_percent=cgst_percent, # Expecting Decimal
        sgst_percent=sgst_percent  # Expecting Decimal
        # id (PK), is_active, created_at, updated_at are handled by CommonModel
    )
    db.add(doc_info)
    db.commit()
    db.refresh(doc_info)
    logger.info(f"Created DocumentInfo record (PK {doc_info.id}) for Document PK {parent_document.id} (business_id {doc_business_id}).")
    return doc_info


def get_document_info_by_parent_doc_pk(db: Session, parent_document_pk: int) -> Optional[DocumentInfoModel]:
    """
    Retrieves DocumentInfo by the parent Document's primary key (integer id).
    """
    return db.query(DocumentInfoModel).filter(DocumentInfoModel.document_fk_id == parent_document_pk).first()

# Original functions to review and map/remove:
# get_month -> get_month_name (corrected logic)
# generate_presigned_url -> generate_s3_presigned_url (standardized)
# create_document_inprogress -> create_initial_document_record
# update_document_status_util -> update_document_status_and_reason
# get_document_by_id -> get_document_by_business_id
# get_current_month_docs -> get_documents_for_user_and_period
# get_current_month_all_user_docs -> get_all_documents_for_period_and_status
# build_object_key -> build_s3_object_key
# get_document_details_by_gst_and_id -> check_duplicate_gst_for_user (logic significantly changed)
# mark_document_duplicate -> (covered by update_document_status_and_reason)
# get_document_info_by_id -> get_document_info_by_parent_doc_pk (or similar based on need)
# create_document_info -> create_document_info_record