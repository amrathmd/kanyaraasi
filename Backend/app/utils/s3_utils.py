import boto3
import os

# Configure AWS region (ideally through environment variable or AWS config)
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")  # Default to Mumbai if not set
S3_BUCKET_NAME = "kanyaraasi-hugohub"  # Replace with your bucket name

# Initialize the S3 client
s3_client = boto3.client("s3", region_name=AWS_REGION)

def upload_file_to_s3(file_path, object_key):
    """Uploads a file to the specified S3 bucket and object key."""
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, object_key)
        print(f"File '{file_path}' uploaded to 's3://{S3_BUCKET_NAME}/{object_key}'")
        return f"s3://{S3_BUCKET_NAME}/{object_key}"
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

def download_file_from_s3(object_key, local_file_path):
    """Downloads a file from the specified S3 bucket and object key to a local path."""
    try:
        s3_client.download_file(S3_BUCKET_NAME, object_key, local_file_path)
        print(f"File 's3://{S3_BUCKET_NAME}/{object_key}' downloaded to '{local_file_path}'")
        return local_file_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

def list_objects_in_s3(prefix=None):
    """Lists objects in the specified S3 bucket with an optional prefix."""
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
        objects = [obj['Key'] for obj in response.get('Contents', [])]
        print(f"Objects in 's3://{S3_BUCKET_NAME}/{prefix if prefix else ''}': {objects}")
        return objects
    except Exception as e:
        print(f"Error listing objects: {e}")
        return []

def get_object_url_from_s3(object_key):
    """Generates a presigned URL for accessing an object in S3 (for temporary access)."""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': object_key},
            ExpiresIn=3600  # URL expires in 1 hour (adjust as needed)
        )
        print(f"Presigned URL for 's3://{S3_BUCKET_NAME}/{object_key}': {url}")
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

