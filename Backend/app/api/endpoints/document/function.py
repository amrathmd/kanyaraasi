import boto3

from app.utils.constant.globals import DocumentStatus
from app.utils.s3_utils import AWS_REGION
from sqlalchemy.orm import Session
from app.models import document as DocumentModal

AWS_REGION = "us-east-1"
month_names = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

def get_month(number: int) -> str:
    return month_names[number]

def generate_presigned_url(
        bucket_name: str,
        object_key: str,
        content_type : str,
        expiration_seconds: int = 3600,
):
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    try:
        params = {"Bucket": bucket_name, "Key": object_key, "ContentType": content_type}

        url = s3_client.generate_presigned_url(
            "put_object", Params=params, ExpiresIn=expiration_seconds
        )
        print(f"Presigned URL for s3://{bucket_name}/{object_key}): {url}")
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

def create_document_inprogress(db :Session,document_id:str,extension:str, user_id:str,year:str,month:str,email:str ):
    document = DocumentModal.Document(
        document_id=document_id,
        extension=extension,
        email=email,
        user_id=user_id,
        year=year,
        month=month,
        status=DocumentStatus.INPROGRESS
    )
    db.add(document)
    db.commit()
    db.refresh(document)

def update_document_status_util(db: Session,document_id:str):
    document: DocumentModal = db.query(DocumentModal.Document).filter(DocumentModal.Document.document_id == document_id).first()
    if document.status == DocumentStatus.INPROGRESS:
        document.status = DocumentStatus.UPLOADED
        db.commit()
        db.refresh(document)
        return True

def get_document_by_id(db: Session,document_id:str):
    return db.query(DocumentModal.Document).filter(DocumentModal.Document.document_id == document_id).first()