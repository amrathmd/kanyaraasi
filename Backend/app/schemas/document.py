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