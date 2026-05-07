"""
Local filesystem storage endpoints – used in development instead of S3.
Only active when LOCAL_STORAGE_PATH is set.
"""
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
from app.services.s3 import save_upload

router = APIRouter()


def _local_path(bucket: str, key: str) -> str:
    return os.path.join(settings.local_storage_path, bucket, key)


@router.put("/api/v1/storage/upload/{bucket}/{key:path}")
async def upload_file(bucket: str, key: str, request: Request):
    if not settings.local_storage_path:
        raise HTTPException(status_code=404)
    data = await request.body()
    path = _local_path(bucket, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return {"ok": True, "key": key}


@router.get("/api/v1/storage/files/{bucket}/{key:path}")
async def serve_file(bucket: str, key: str):
    if not settings.local_storage_path:
        raise HTTPException(status_code=404)
    path = _local_path(bucket, key)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
