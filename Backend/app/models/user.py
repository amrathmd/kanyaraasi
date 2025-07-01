# user.py
# Defines the SQLAlchemy model for users.

from sqlalchemy import Column, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship # Added for relationship
# from enum import Enum as PythonEnum # Not strictly necessary if UserRole is already an Enum

# Ensure all model imports for relationships are present, even if only for type hinting or relationship definition
# from .account import Account # Not strictly needed if using string "Account" in relationship
# from .document import Document # Not strictly needed if using string "Document" in relationship

from app.core.database import Base
from .common import CommonModel # Import CommonModel to inherit common fields
from app.utils.constant.globals import UserRole # Defines the UserRole enum


class User(CommonModel): # Inherit from CommonModel
    """
    SQLAlchemy model representing a user in the system.

    Inherits `is_active`, `created_at`, `updated_at` from CommonModel.
    The `id` from CommonModel (Integer) is overridden here by a String `id`.

    Attributes:
        id (String): Unique identifier for the user. Overrides CommonModel's Integer ID.
        email (String): The user's email address. Must be unique.
        password (String): The user's hashed password.
        role (UserRole): The role of the user (e.g., USER, ADMIN). Defaults to UserRole.USER.
        name (String, optional): The user's full name or display name.

        accounts (relationship): One-to-many relationship to the Account model.
                                 Links to the user's yearly account balances.
        documents (relationship): One-to-many relationship to the Document model.
                                  Links to the documents uploaded by the user.
    """
    __tablename__ = "users"

    # Overriding the 'id' from CommonModel to be a String.
    # This means the primary key for 'users' table will be this String 'id'.
    id = Column(String, primary_key=True, index=True, unique=True, comment="Unique identifier for the user (String).")

    email = Column(String, unique=True, index=True, nullable=False, comment="User's email address (must be unique).")
    password = Column(String, nullable=False, comment="Hashed password for the user.")

    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.USER, nullable=False, comment="Role of the user (e.g., USER, ADMIN).")

    name = Column(String, nullable=True, comment="Full name or display name of the user.")

    # --- Relationships ---
    # Bidirectional relationship with Account model
    # 'cascade="all, delete-orphan"' ensures related accounts are deleted if this user is deleted.
    # 'passive_deletes=True' can be useful with DB-level ON DELETE CASCADE.
    accounts = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        doc="User's financial accounts, one record per year."
    )

    # Bidirectional relationship with Document model
    documents = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        doc="Documents uploaded by the user."
    )


    def __repr__(self):
        """
        Provides a string representation of the User instance.
        """
        active_status = "active" if self.is_active else "inactive"
        return f"<User(id='{self.id}', email='{self.email}', role='{self.role.name if self.role else None}', status='{active_status}')>"

# metadata = Base.metadata # This line is generally not needed here.

