# common.py
# Defines a common base model with shared fields for other SQLAlchemy models.
# This helps in maintaining consistency and reducing redundancy across different models.

from sqlalchemy import Column, Boolean, Integer, DateTime, func
# import uuid # Not currently used due to id being Integer. Kept for potential future use if UUIDs are re-enabled.
from app.core.database import Base


class CommonModel(Base):
    """
    An abstract base model that provides common fields for all other models.

    Attributes:
        id (Integer): The primary key for the table, auto-incrementing.
                      A commented-out UUID version is present, suggesting a potential previous or alternative design.
        is_active (Boolean): A flag to indicate if the record is active or soft-deleted. Defaults to True.
        created_at (DateTime): Timestamp of when the record was created. Defaults to the current server time.
        updated_at (DateTime): Timestamp of when the record was last updated.
                               Defaults to the current server time on creation and updates automatically on modification.
    """
    __abstract__ = True  # Indicates that this class should not be mapped to a database table itself.

    # Primary key: Currently an Integer.
    # A previous implementation or consideration for UUID primary keys is noted below.
    # If switching to UUIDs, ensure `default=lambda: str(uuid.uuid4())` is appropriate or use `default=uuid.uuid4` if the column type is `UUID`.
    # id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    id = Column(Integer, primary_key=True, index=True, comment="Primary key for the record, auto-incrementing integer.")

    is_active = Column(Boolean, default=True, nullable=False, comment="Flag to indicate if the record is active (True) or soft-deleted (False).")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp of when the record was created (UTC)."
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp of when the record was last updated (UTC)."
    )

    def __repr__(self):
        """
        Provides a string representation of the model instance, primarily for debugging.
        Shows the class name and the id of the instance.
        """
        return f"<{self.__class__.__name__}(id={self.id})>"

