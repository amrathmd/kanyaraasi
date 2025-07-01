# document.py
# Pydantic schemas for document-related data validation and serialization.

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.utils.constant.globals import DocumentStatus, Month # Assuming Month might be used

# --- Schemas for Presigned URL Operations ---

class PresignedUrlRequest(BaseModel):
    """
    Schema for requesting a presigned URL for uploading a document.
    """
    content_type: str = Field(..., example="image/jpeg", description="MIME type of the file to be uploaded.")
    # file_name: Optional[str] = Field(None, example="invoice.jpg", description="Original name of the file.") # Could be useful

class PresignedUrlResponse(BaseModel):
    """
    Schema for the response containing the presigned URL and document identifier.
    The `document_code` seems to be the `document_id` (business identifier) from the Document model.
    """
    presigned_url: HttpUrl = Field(..., example="https://s3.amazonaws.com/bucket/...", description="The presigned URL for uploading the file.")
    document_id: str = Field(..., example="doc_uuid_or_unique_code", description="Unique identifier assigned to this document for tracking.")


# --- Base Document Schema ---

class DocumentBase(BaseModel):
    """
    Base schema for core document attributes.
    """
    # document_id is the business identifier, not the integer PK 'id' from CommonModel
    document_id: str = Field(..., example="doc_uuid_xyz123", description="Unique business identifier for the document.")
    month: str = Field(..., example="JANUARY", description="Month relevant to the document (e.g., 'JANUARY', '01').") # Consider Month enum
    year: str = Field(..., example="2023", pattern=r"^\d{4}$", description="Year relevant to the document (e.g., '2023').")

    class Config:
        orm_mode = True # For Pydantic V1; use from_attributes = True for V2


# --- Schema for Document Creation (metadata after upload) ---
# This might be used internally or if metadata is sent separately after blob upload.
class DocumentCreate(DocumentBase):
    """
    Schema for creating a document record after the file is uploaded.
    """
    user_id: str = Field(..., example="user_uuid_abc789", description="Identifier of the user uploading the document.")
    extension: str = Field(..., example="pdf", description="File extension of the document.")
    email: Optional[str] = Field(None, example="user@example.com", description="User's email (potentially redundant, consider linking via user_id).")
    # Status will likely default to PENDING in the model or service layer.

# --- Schema for Document Update (e.g., status changes) ---

class DocumentStatusUpdate(BaseModel):
    """
    Schema for updating a document's status.
    References document by its business identifier `document_id`.
    """
    # document_id refers to the business identifier string
    document_id: str = Field(..., example="doc_uuid_xyz123", description="Business identifier of the document to update.")
    status: DocumentStatus = Field(..., example=DocumentStatus.APPROVED, description="New status for the document.")
    reason: Optional[str] = Field(None, example="Invoice details verified.", description="Optional reason for the status change.")


# --- Schemas for Document Responses ---

class DocumentResponse(DocumentBase):
    """
    Schema for representing a document in API responses.
    Includes fields from CommonModel.
    """
    id: int = Field(..., example=123, description="Primary key of the document record.")
    user_id: str = Field(..., example="user_uuid_abc789", description="Identifier of the user who owns the document.")
    extension: str = Field(..., example="pdf", description="File extension.")
    status: DocumentStatus = Field(..., example=DocumentStatus.PENDING, description="Current status of the document.")
    reason: Optional[str] = Field(None, example="Awaiting verification.", description="Reason associated with the current status.")
    # url: Optional[HttpUrl] = Field(None, example="s3://bucket/path/to/doc.pdf", description="URL to access the document. This might be a presigned URL for downloads or a direct link if public.")
    # The 'url' field from the original 'Document' schema: its generation and nature need to be defined.
    # If it's a download URL, it's often generated on-demand.
    url_for_download: Optional[HttpUrl] = Field(None, description="A (potentially presigned) URL to download the document content.") # Added field

    is_active: bool = Field(..., description="Indicates if the document record is active (not soft-deleted).")
    created_at: datetime = Field(..., description="Timestamp of when the document record was created.")
    updated_at: datetime = Field(..., description="Timestamp of when the document record was last updated.")
    email: Optional[str] = Field(None, example="user@example.com", description="User's email (potentially redundant).")


class DocumentListResponse(BaseModel):
    """
    Schema for a list of documents.
    """
    documents: List[DocumentResponse] = Field(..., description="A list of document records.")


# --- Schema for Detailed Document View (Document + ExtractedInfo) ---

class DocumentInfoBase(BaseModel): # For fields from DocumentInfo model
    """
    Base schema for document information extracted by OCR/processing.
    """
    gst_in: Optional[str] = Field(None, example="22AAAAA0000A1Z5", description="GST Identification Number from the document.")
    total_amount: Optional[Decimal] = Field(None, decimal_places=2, example=Decimal("1250.75"), description="Total amount from the document.")
    cgst_percent: Optional[Decimal] = Field(None, decimal_places=2, example=Decimal("9.00"), description="CGST percentage from the document.")
    sgst_percent: Optional[Decimal] = Field(None, decimal_places=2, example=Decimal("9.00"), description="SGST percentage from the document.")

    class Config:
        orm_mode = True

class DocumentDetailResponse(DocumentResponse): # Inherits fields from DocumentResponse
    """
    Schema for a detailed view of a document, including extracted information.
    Combines fields from Document and DocumentInfo models.
    """
    # Fields from DocumentInfo are added here.
    # If DocumentInfo is a separate object:
    # extracted_info: Optional[DocumentInfoBase] = Field(None, description="Extracted information from the document.")
    # Or, flatten them:
    gst_in: Optional[str] = Field(None, example="22AAAAA0000A1Z5", description="GSTIN from document details.")
    total_amount: Optional[Decimal] = Field(None, decimal_places=2, example=Decimal("1250.75"), description="Total amount from document details.")
    cgst_percent: Optional[Decimal] = Field(None, decimal_places=2, example=Decimal("9.00"), description="CGST from document details.")
    sgst_percent: Optional[Decimal] = Field(None, decimal_places=2, example=Decimal("9.00"), description="SGST from document details.")

    # Note: `email` is already in DocumentResponse.
    # The original `DocumentDetails.gst_number` renamed to `gst_in` for consistency with DocumentInfo model.


class DocumentDetailListResponse(BaseModel):
    """
    Schema for a list of detailed document views.
    """
    documents: List[DocumentDetailResponse] = Field(..., description="A list of detailed document records.")


# --- Mapping Original Schemas to New Ones ---
# GetPresignedUrl -> PresignedUrlRequest
# SendPresignedUrl -> PresignedUrlResponse (document_code -> document_id)
# Document -> DocumentResponse (with CommonModel fields, url needs clarification)
# GetDocuments -> DocumentListResponse
# UpdateDocStatus -> DocumentStatusUpdate (document_id is business id)
# DocumentDetails -> DocumentDetailResponse (aligns with Document & DocumentInfo models, uses Decimal)
# DocumentDetailsList -> DocumentDetailListResponse