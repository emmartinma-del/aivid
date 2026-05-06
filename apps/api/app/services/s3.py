import boto3
from botocore.config import Config
from app.config import settings


def get_s3_client():
    kwargs = {
        "aws_access_key_id": settings.s3_access_key_id,
        "aws_secret_access_key": settings.s3_secret_access_key,
        "region_name": settings.s3_region,
        "config": Config(signature_version="s3v4"),
    }
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    return boto3.client("s3", **kwargs)


def generate_presigned_upload_url(bucket: str, key: str, mime_type: str, expires_in: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket, "Key": key, "ContentType": mime_type},
        ExpiresIn=expires_in,
    )


def generate_presigned_download_url(bucket: str, key: str, expires_in: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def get_public_url(bucket: str, key: str) -> str:
    if settings.cloudfront_domain:
        return f"https://{settings.cloudfront_domain}/{key}"
    if settings.s3_public_url:
        return f"{settings.s3_public_url}/{bucket}/{key}"
    return f"https://{bucket}.s3.{settings.s3_region}.amazonaws.com/{key}"
