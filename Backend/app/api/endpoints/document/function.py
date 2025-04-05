from datetime import datetime

import boto3

from app.models import document_info as DocInfo
from app.utils.constant.globals import DocumentStatus
from app.utils.s3_utils import AWS_REGION
from sqlalchemy.orm import Session
from app.models import document as DocumentModal
from sqlalchemy import extract

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
        content_type : str = "",
        param_type :str = "put_object",
        expiration_seconds: int = 3600,
):
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    try:
        params = {"Bucket": bucket_name, "Key": object_key, "ContentType": content_type}
        if param_type == "put_object":
            params = {"Bucket": bucket_name, "Key": object_key, "ContentType": content_type}
        else:
            params = {"Bucket": bucket_name, "Key": object_key}

        url = s3_client.generate_presigned_url(
            param_type, Params=params, ExpiresIn=expiration_seconds
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

def get_current_month_docs(db:Session,user_id:str):
    now = datetime.now()
    documents = db.query(DocumentModal.Document).filter(
        DocumentModal.Document.user_id == user_id,
        extract('year', DocumentModal.Document.year == str(now.year)),
        extract('month',DocumentModal.Document.month == get_month(now.month))
        # extract('status' , DocumentModal.Document.status != DocumentStatus.INPROGRESS)
    ).all()
    return documents

def build_object_key(email:str,document_id: str,extension:str) -> str:
    year = str(datetime.now().year)
    month = get_month(datetime.now().month)


    return  f"{year}/{month}/{email}/{document_id}.{extension}"

def get_document_details_by_gst_and_id(db: Session,gst_in:str, doc_id:str):
    document = (db.query(DocInfo.DocumentInfo).filter(DocInfo.DocumentInfo.gst_in == gst_in)
                .filter(DocInfo.DocumentInfo.document_id == doc_id)
                .first())

    if not document:
        return False
    return True

def mark_document_duplicate(db: Session,document_id:str):
    document: DocumentModal = db.query(DocumentModal.Document).filter(DocumentModal.Document.document_id == document_id).first()
    document.status = DocumentStatus.REJECTED
    document.reason = "Duplicate GSI number found"
    db.commit()
    db.refresh(document)
    return True

def create_document_info(db :Session,document_id:str,gst_in:str, total_amount:str,cgst_percent:str,sgst_percent:str):
    document = DocInfo.DocumentInfo(
        document_id=document_id,
        gst_in=gst_in,
        total_amount=total_amount,
        cgst_percent=cgst_percent,
        sgst_percent=sgst_percent,
    )
    db.add(document)
    db.commit()
    db.refresh(document)