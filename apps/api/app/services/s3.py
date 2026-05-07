"""
S3 service with local filesystem fallback for development.
When LOCAL_STORAGE_PATH is set in config, files are stored on disk instead of S3.
"""
import os
import shutil
import boto3
from botocore.config import Config
from app.config import settings


def _is_local() -> bool:
    return bool(settings.local_storage_path)


def _local_path(bucket: str, key: str) -> str:
    path = os.path.join(settings.local_storage_path, bucket, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def get_s3_client():
    kwargs = {
        "aws_access_key_id": settings.s3_access_key_id or "dev",
        "aws_secret_access_key": settings.s3_secret_access_key or "dev",
        "region_name": settings.s3_region,
        "config": Config(signature_version="s3v4"),
    }
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    return boto3.client("s3", **kwargs)


def generate_presigned_upload_url(bucket: str, key: str, mime_type: str, expires_in: int = 3600) -> str:
    if _is_local():
        # Return an API endpoint that accepts the file upload directly
        return f"{settings.frontend_url.replace('3000', '8000')}/api/v1/storage/upload/{bucket}/{key}"
    client = get_s3_client()
    return client.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket, "Key": key, "ContentType": mime_type},
        ExpiresIn=expires_in,
    )


def generate_presigned_download_url(bucket: str, key: str, expires_in: int = 3600) -> str:
    if _is_local():
        return get_public_url(bucket, key)
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def get_public_url(bucket: str, key: str) -> str:
    if _is_local():
        return f"http://localhost:8000/api/v1/storage/files/{bucket}/{key}"
    if settings.cloudfront_domain:
        return f"https://{settings.cloudfront_domain}/{key}"
    if settings.s3_public_url:
        return f"{settings.s3_public_url}/{bucket}/{key}"
    return f"https://{bucket}.s3.{settings.s3_region}.amazonaws.com/{key}"


def upload_file_local(src_path: str, bucket: str, key: str, content_type: str = "application/octet-stream") -> None:
    """Used by Celery worker to 'upload' finished video to local storage."""
    if _is_local():
        dest = _local_path(bucket, key)
        shutil.copy2(src_path, dest)
    else:
        client = get_s3_client()
        client.upload_file(src_path, bucket, key, ExtraArgs={"ContentType": content_type})


def download_file_local(bucket: str, key: str, dest_path: str) -> None:
    """Used by Celery worker to download assets from local storage or S3."""
    if _is_local():
        src = _local_path(bucket, key)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src, dest_path)
    else:
        client = get_s3_client()
        client.download_file(bucket, key, dest_path)


def save_upload(data: bytes, bucket: str, key: str) -> None:
    """Save an uploaded file directly (used by local storage upload endpoint)."""
    path = _local_path(bucket, key)
    with open(path, "wb") as f:
        f.write(data)
