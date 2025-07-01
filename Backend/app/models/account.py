# account.py
# Defines the SQLAlchemy model for user accounts, tracking balances per year.

from sqlalchemy import Column, String, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base
from .common import CommonModel # Import CommonModel to inherit common fields


class Account(CommonModel): # Inherit from CommonModel
    """
    SQLAlchemy model representing a user's financial account information for a specific year.

    Inherits common fields (id, is_active, created_at, updated_at) from CommonModel.
    The `id` from CommonModel will serve as the primary key.
    A unique constraint is added for the combination of `user_id` and `year`
    to maintain the business logic of one account record per user per year.

    Attributes:
        user_id (String): Foreign key referencing the User table's id. Part of a composite unique key.
        year (String): The year for which this account information is valid (e.g., "2023"). Part of a composite unique key.
        total_balance (DECIMAL): The total allocated balance for the user for that year.
        available_balance (DECIMAL): The remaining available balance for the user for that year.
        user (relationship): SQLAlchemy relationship to the User model.
    """
    __tablename__ = "account"

    # user_id now references users.id (assuming users table has a String id)
    # If users.id is an Integer, this should be Integer as well.
    # This requires the User model to have an 'id' column.
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True, comment="Identifier of the user this account belongs to.")

    year = Column(String(4), nullable=False, index=True, comment="The financial year for this account record (e.g., '2023').") # Assuming year is like 'YYYY'

    # For DECIMAL types, it's good practice to specify precision and scale.
    # Example: DECIMAL(precision=10, scale=2) for up to 10 digits, 2 after decimal.
    # Using default precision/scale for now, but this should be reviewed based on requirements.
    total_balance = Column(DECIMAL, nullable=False, default=0.0, comment="Total allocated balance for the year.")
    available_balance = Column(DECIMAL, nullable=False, default=0.0, comment="Currently available balance for the year.")

    # Define a relationship to the User model
    # The back_populates string should match the relationship name in the User model if a bidirectional relationship is defined there.
    user = relationship("User", back_populates="accounts") # Assuming "accounts" is the relationship name in User model

    # Define a unique constraint for user_id and year, instead of a composite primary key,
    # as CommonModel already provides an 'id' primary key.
    __table_args__ = (
        UniqueConstraint('user_id', 'year', name='uq_user_year'),
        # ForeignKeyConstraint(['user_id'], ['users.id']) # This is implicitly created by ForeignKey in user_id
    )

    def __repr__(self):
        """
        Provides a string representation of the Account instance.
        """
        return f"<Account(id={self.id}, user_id='{self.user_id}', year='{self.year}', available='{self.available_balance}')>"

# In User model (app/models/user.py), you would add:
# from sqlalchemy.orm import relationship
# accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
# This creates a bidirectional relationship and ensures accounts are deleted if a user is deleted.
