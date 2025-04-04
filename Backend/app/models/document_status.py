from sqlalchemy import Column, String, Enum, DECIMAL, Boolean

from app.core.database import Base
from app.models.common import CommonModel  # Assuming CommonModel exists
from app.utils.constant.globals import Month, DocumentStatus

class DocumentStatus(Base):
    __tablename__ = "documents_status"

    document_id = Column(String,unique=True,primary_key=True)
    gst_in = Column(String)
    total_amount = Column(DECIMAL)
    cgst_percent = Column(DECIMAL)
    sgst_percent = Column(DECIMAL)
