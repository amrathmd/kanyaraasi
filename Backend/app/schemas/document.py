from pydantic import BaseModel

from app.utils.constant.globals import DocumentStatus


class GetPresignedUrl(BaseModel):
    content_type : str

class SendPresignedUrl(BaseModel):
    presigned_url :str
    document_code : str

class Document(BaseModel):
    status : DocumentStatus
    document_id: str
    year : str
    month: str
    reason: str
    url : str

class GetDocuments(BaseModel):
    documents : list[Document]

class UpdateDocStatus(BaseModel):
    document_id: str
    status: DocumentStatus

class DocumentDetails(BaseModel):
    document_id: str
    status: DocumentStatus
    year: str
    month: str
    email: str
    gst_number: str
    total_amount: float
    cgst_percent: float
    sgst_percent: float

class DocumentDetailsList(BaseModel):
    documents: list[DocumentDetails]