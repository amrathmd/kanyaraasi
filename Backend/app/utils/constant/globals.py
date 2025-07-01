# globals.py
# Defines global enumerations and constants used throughout the application.

from enum import Enum as PythonEnum

class UserRole(str, PythonEnum):
    """
    Enumeration for user roles within the system.
    Inherits from str to allow easy string comparison and serialization.
    """
    USER = "USER"    # Regular user with standard privileges.
    ADMIN = "ADMIN"  # Administrator with elevated privileges.

class Month(str, PythonEnum):
    """
    Enumeration for months of the year.
    Values are lowercase month names. This casing might be relevant for
    database storage or external integrations; change with caution.
    """
    JANUARY = "january"
    FEBRUARY = "february"
    MARCH = "march"
    APRIL = "april"
    MAY = "may"
    JUNE = "june"
    JULY = "july"
    AUGUST = "august"
    SEPTEMBER = "september"
    OCTOBER = "october"
    NOVEMBER = "november"
    DECEMBER = "december"

class DocumentStatus(str, PythonEnum):
    """
    Enumeration for the processing status of documents.
    """
    PENDING_UPLOAD = "PENDING_UPLOAD" # Document record created, presigned URL generated, awaiting client upload.
    INPROGRESS = "INPROGRESS"        # Original status, usage might need clarification. Could be OCR processing.
                                     # Retained for compatibility, but PENDING_OCR or PROCESSING might be clearer.
    UPLOADED = "UPLOADED"            # File successfully uploaded to S3, pending further processing (e.g., OCR).
    PENDING_REVIEW = "PENDING_REVIEW"# Document processed by OCR, awaiting admin/manual review.
    APPROVED = "APPROVED"            # Document has been reviewed and approved.
    REJECTED = "REJECTED"            # Document has been reviewed and rejected.
    # Consider adding FAILED_OCR or FAILED_PROCESSING if needed.

# Example of how these enums are used in SQLAlchemy models:
# from sqlalchemy import Column, Enum as SQLAlchemyEnum
# from .globals import UserRole
# role = Column(SQLAlchemyEnum(UserRole), default=UserRole.USER)

# Example of usage in Pydantic schemas:
# from pydantic import BaseModel, Field
# from .globals import DocumentStatus
# class Document(BaseModel):
#     status: DocumentStatus = Field(..., example=DocumentStatus.APPROVED)
