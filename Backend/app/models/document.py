# document.py
# Defines the SQLAlchemy model for documents.

from sqlalchemy import Column, String, Integer, Boolean, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship

# Ensure DocumentInfo is imported if directly referenced in relationship type hint, though string "DocumentInfo" is fine.
# from .document_info import DocumentInfo

from app.core.database import Base
from .common import CommonModel # Inherit common fields
from app.utils.constant.globals import Month, DocumentStatus # Enums for month and status


class Document(CommonModel): # Inherit from CommonModel
    """
    SQLAlchemy model representing a document uploaded by a user.

    Inherits common fields (id, is_active, created_at, updated_at) from CommonModel.
    The `id` from CommonModel serves as the primary key.
    The original `document_id` is kept as a unique business identifier.

    Attributes:
        user_id (String): Foreign key referencing the User table's id.
        month (String): The month relevant to the document.
        year (String): The year relevant to the document (e.g., "2023").
        document_id (String): A unique business identifier for the document.
        extension (String): The file extension of the document (e.g., "pdf", "jpeg").
        status (DocumentStatus): The processing status of the document.
        reason (String, optional): A reason or comment, e.g., for rejection.
        email (String, optional): Email of the user (potentially redundant, consider removing).

        user (relationship): Many-to-one relationship to the User model.
        document_info (relationship): One-to-one relationship to the DocumentInfo model,
                                      containing extracted details from this document.
    """
    __tablename__ = "documents"

    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True, comment="Identifier of the user who owns this document.")

    month = Column(String, nullable=False, comment="Month relevant to the document (e.g., name or number). Consider Enum.")
    year = Column(String(4), nullable=False, comment="Year relevant to the document (e.g., '2023').")

    document_id = Column(String, unique=True, index=True, nullable=False, comment="Unique business identifier for the document (not the PK).")

    extension = Column(String(10), nullable=False, comment="File extension of the document (e.g., 'pdf', 'png').")

    status = Column(SQLAlchemyEnum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING, comment="Processing status of the document.")

    reason = Column(String, nullable=True, comment="Optional reason, e.g., for rejection or clarification.")

    email = Column(String, nullable=True, comment="Email of the user (potentially redundant if user relationship exists and is sufficient).")

    # --- Relationships ---
    # Many-to-one relationship with User
    user = relationship("User", back_populates="documents")

    # One-to-one relationship with DocumentInfo
    # `uselist=False` makes this a scalar attribute (one-to-one).
    # `cascade="all, delete-orphan"` ensures DocumentInfo is deleted if this Document is deleted.
    # `passive_deletes=True` can be useful with DB-level ON DELETE CASCADE.
    document_info = relationship(
        "DocumentInfo",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        doc="Extracted information associated with this document."
    )


    def __repr__(self):
        """
        Provides a string representation of the Document instance.
        """
        return f"<Document(id={self.id}, doc_id='{self.document_id}', user_id='{self.user_id}', status='{self.status.name if self.status else None}')>"

# Note: The 'deleted' column was removed as 'is_active' from CommonModel handles this.
# Note: The relationship in User model 'documents' should correctly back-populate this.
# Note: The relationship in DocumentInfo model 'document' should correctly back-populate this.
