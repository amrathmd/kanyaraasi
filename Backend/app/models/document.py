from sqlalchemy import Column, String, Enum, Integer, Boolean

from app.core.database import Base
from app.models.common import CommonModel  # Assuming CommonModel exists
from app.utils.constant.globals import Month, DocumentStatus

class Document(Base):
    __tablename__ = "documents"

    user_id = Column(String, unique=True, index=True)
    month = Column(Enum(Month))
    year = Column(Integer)
    document_id = Column(String, primary_key=True)
    s3_path = Column(String, unique=True)
    status = Column(Enum(DocumentStatus))
    reason = Column(String)
    deleted = Column(Boolean)
