from sqlalchemy import Column, String, Enum, Integer, Boolean

from app.core.database import Base
from app.models.common import CommonModel  # Assuming CommonModel exists
from app.utils.constant.globals import Month, DocumentStatus

class Document(Base):
    __tablename__ = "documents"

    user_id = Column(String)
    month = Column(String)
    year = Column(String)
    document_id = Column(String, primary_key=True)
    extension = Column(String)
    status = Column(Enum(DocumentStatus))
    reason = Column(String,nullable=True)
    deleted = Column(Boolean,default=False)
    email = Column(String)
