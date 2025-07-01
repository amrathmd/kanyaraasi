# s3_utils.py
# Utility functions for interacting with AWS S3.

import logging
from typing import List, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

# Import S3 configuration from central settings
# These are expected to be defined in app.core.settings.py
from app.core.settings import AWS_S3_REGION_NAME, S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# Setup logger for this module
logger = logging.getLogger(__name__)

# Initialize the S3 client
# Ensure AWS credentials and region are configured, ideally via environment variables
# or IAM roles if running on EC2/ECS.
# For local development, ensure AWS CLI is configured or provide credentials directly (less secure for prod).
try:
    # If AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are provided in settings, use them.
    # Otherwise, boto3 will attempt to find credentials via environment variables, shared credential file, or IAM role.
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        s3_client = boto3.client(
            "s3",
            region_name=AWS_S3_REGION_NAME,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    else:
        s3_client = boto3.client("s3", region_name=AWS_S3_REGION_NAME)
    logger.info(f"S3 client initialized for region {AWS_S3_REGION_NAME} and bucket {S3_BUCKET_NAME}.")
except (NoCredentialsError, PartialCredentialsError):
    logger.error("AWS credentials not found. Please configure AWS credentials.")
    s3_client = None # Indicate client initialization failed
except Exception as e:
    logger.error(f"Failed to initialize S3 client: {e}")
    s3_client = None


class S3UtilError(Exception):
    """Custom exception for S3 utility errors."""
    pass


def upload_file_to_s3(file_path: str, object_key: str) -> Optional[str]:
    """
    Uploads a file to the configured S3 bucket.

    Args:
        file_path: The local path to the file to upload.
        object_key: The desired key (path) for the object in S3.

    Returns:
        The S3 URI of the uploaded object if successful, else None.
        Raises S3UtilError on failure.
    """
    if not s3_client:
        logger.error("S3 client not initialized. Cannot upload file.")
        raise S3UtilError("S3 client not initialized.")
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, object_key)
        s3_uri = f"s3://{S3_BUCKET_NAME}/{object_key}"
        logger.info(f"File '{file_path}' uploaded to '{s3_uri}'")
        return s3_uri
    except FileNotFoundError:
        logger.error(f"Upload failed: Local file '{file_path}' not found.")
        raise S3UtilError(f"Local file '{file_path}' not found.")
    except ClientError as e:
        logger.error(f"Error uploading file to S3 ('{object_key}'): {e}")
        raise S3UtilError(f"S3 ClientError during upload: {e}")
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"Unexpected error uploading file '{file_path}': {e}")
        raise S3UtilError(f"Unexpected error during upload: {e}")


def download_file_from_s3(object_key: str, local_file_path: str) -> Optional[str]:
    """
    Downloads a file from the configured S3 bucket to a local path.

    Args:
        object_key: The key of the object in S3.
        local_file_path: The local path to save the downloaded file.

    Returns:
        The local file path if download is successful, else None.
        Raises S3UtilError on failure.
    """
    if not s3_client:
        logger.error("S3 client not initialized. Cannot download file.")
        raise S3UtilError("S3 client not initialized.")
    try:
        s3_client.download_file(S3_BUCKET_NAME, object_key, local_file_path)
        logger.info(f"File 's3://{S3_BUCKET_NAME}/{object_key}' downloaded to '{local_file_path}'")
        return local_file_path
    except ClientError as e:
        logger.error(f"Error downloading file from S3 ('{object_key}'): {e}")
        # Check for specific errors like "NoSuchKey"
        if e.response['Error']['Code'] == '404': # Or 'NoSuchKey' depending on boto version/method
             raise S3UtilError(f"S3 object '{object_key}' not found in bucket '{S3_BUCKET_NAME}'.")
        raise S3UtilError(f"S3 ClientError during download: {e}")
    except Exception as e:
        logger.error(f"Unexpected error downloading file '{object_key}': {e}")
        raise S3UtilError(f"Unexpected error during download: {e}")


def list_objects_in_s3(prefix: Optional[str] = None) -> List[str]:
    """
    Lists objects in the configured S3 bucket, optionally filtered by a prefix.

    Args:
        prefix: Optional prefix to filter objects.

    Returns:
        A list of object keys. Returns an empty list on failure.
    """
    if not s3_client:
        logger.error("S3 client not initialized. Cannot list objects.")
        return [] # Or raise S3UtilError("S3 client not initialized.")
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix or '')
        objects = [obj['Key'] for obj in response.get('Contents', [])]
        logger.info(f"Found {len(objects)} objects in 's3://{S3_BUCKET_NAME}/{prefix or ''}'")
        return objects
    except ClientError as e:
        logger.error(f"Error listing objects from S3 (prefix '{prefix}'): {e}")
        return [] # Or raise S3UtilError
    except Exception as e:
        logger.error(f"Unexpected error listing S3 objects: {e}")
        return [] # Or raise S3UtilError

def generate_presigned_url(
    object_key: str,
    client_method: str = 'get_object', # e.g., 'get_object', 'put_object'
    method_parameters: Optional[dict] = None,
    expires_in: int = 3600 # Default to 1 hour
) -> Optional[str]:
    """
    Generates a presigned URL for an S3 object.
    This is a more generic version. The one in `document/function.py` is specific to its needs.
    Consider consolidating if appropriate.

    Args:
        object_key: The key of the object in S3.
        client_method: The S3 client method to generate URL for (e.g., 'get_object', 'put_object').
        method_parameters: Parameters for the client method (e.g., {'ContentType': 'image/jpeg'} for put_object).
        expires_in: Expiration time for the URL in seconds.

    Returns:
        The presigned URL string, or None on error.
    """
    if not s3_client:
        logger.error("S3 client not initialized. Cannot generate presigned URL.")
        return None # Or raise S3UtilError

    params = method_parameters or {}
    params['Bucket'] = S3_BUCKET_NAME
    params['Key'] = object_key

    try:
        url = s3_client.generate_presigned_url(
            ClientMethod=client_method,
            Params=params,
            ExpiresIn=expires_in
        )
        logger.info(f"Generated presigned URL for '{client_method}' on '{object_key}': {url}")
        return url
    except ClientError as e:
        logger.error(f"Error generating presigned URL for S3 object '{object_key}': {e}")
        return None # Or raise S3UtilError
    except Exception as e:
        logger.error(f"Unexpected error generating presigned URL for '{object_key}': {e}")
        return None # Or raise S3UtilError

# Note: The original get_object_url_from_s3 is now covered by the more generic generate_presigned_url.
# If only 'get_object' URLs are needed from this util, a simpler dedicated function can be kept:
# def get_presigned_download_url(object_key: str, expires_in: int = 3600) -> Optional[str]:
#     return generate_presigned_url(object_key, 'get_object', expires_in=expires_in)

