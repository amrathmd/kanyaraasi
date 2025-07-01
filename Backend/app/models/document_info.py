# document_info.py
# Defines the SQLAlchemy model for storing extracted information from documents.

from sqlalchemy import Column, String, DECIMAL, ForeignKey, Integer # Added Integer for FK
from sqlalchemy.orm import relationship

from app.core.database import Base
from .common import CommonModel # Inherit common fields
# Assuming Document model has 'id' as Integer PK after its refactor.

class DocumentInfo(CommonModel): # Inherit from CommonModel
    """
    SQLAlchemy model representing extracted information from a specific document.
    This typically forms a one-to-one relationship with the Document model.

    Inherits common fields (id, is_active, created_at, updated_at) from CommonModel.
    The `id` from CommonModel serves as the primary key for this table.
    A foreign key `document_fk_id` links to the `id` of the parent Document.
    This foreign key has a unique constraint to enforce the one-to-one relationship.

    Attributes:
        document_fk_id (Integer): Foreign key to the `id` of the related Document. Unique.
        gst_in (String, optional): GST Identification Number extracted from the document.
        total_amount (DECIMAL, optional): Total amount extracted from the document.
        cgst_percent (DECIMAL, optional): CGST percentage extracted.
        sgst_percent (DECIMAL, optional): SGST percentage extracted.
        document (relationship): SQLAlchemy relationship back to the Document model.
    """
    __tablename__ = "documents_info"

    # Foreign key to the Document table's primary key ('id', which is an Integer from CommonModel).
    # This column must be unique to enforce a one-to-one relationship.
    document_fk_id = Column(Integer, ForeignKey("documents.id"), unique=True, nullable=False, index=True, comment="Foreign key to the primary key of the associated document in 'documents' table.")

    gst_in = Column(String(15), index=True, nullable=True, comment="GST Identification Number (e.g., '22AAAAA0000A1Z5').") # Standard GSTIN format

    # For DECIMAL types, specify precision and scale for currency or percentages.
    # Example: DECIMAL(precision=10, scale=2)
    total_amount = Column(DECIMAL, nullable=True, comment="Total amount extracted from the document.")
    cgst_percent = Column(DECIMAL, nullable=True, comment="CGST percentage (e.g., 9 for 9%).")
    sgst_percent = Column(DECIMAL, nullable=True, comment="SGST percentage (e.g., 9 for 9%).")

    # --- Relationship ---
    # One-to-one relationship with Document: DocumentInfo belongs to one Document.
    # `back_populates` should match the relationship name in the Document model.
    document = relationship("Document", back_populates="document_info") # Corrected from document_infos to document_info for one-to-one

    def __repr__(self):
        """
        Provides a string representation of the DocumentInfo instance.
        """
        return f"<DocumentInfo(id={self.id}, document_fk_id={self.document_fk_id}, gst_in='{self.gst_in}')>"

# In Document model (app/models/document.py), you would add for one-to-one:
# from sqlalchemy.orm import relationship
# document_info = relationship("DocumentInfo", back_populates="document", uselist=False, cascade="all, delete-orphan")
# `uselist=False` is key for one-to-one.
