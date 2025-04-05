from sqlalchemy import Column, String, Enum, DECIMAL, Boolean

from app.core.database import Base

class DocumentInfo(Base):
    __tablename__ = "documents_info"

    document_id = Column(String,unique=True,primary_key=True)
    gst_in = Column(String,index=True)
    total_amount = Column(DECIMAL)
    cgst_percent = Column(DECIMAL)
    sgst_percent = Column(DECIMAL)
