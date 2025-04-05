from sqlalchemy import Column, String, DECIMAL, PrimaryKeyConstraint

from app.core.database import Base

class Account(Base):
    __tablename__ = "account"

    user_id = Column(String)
    year = Column(String)
    total_balance = Column(DECIMAL)
    available_balance = Column(DECIMAL)

    # Define the composite primary key
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'year'),
    )
