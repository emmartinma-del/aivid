import uuid
from datetime import datetime
from pydantic import BaseModel


class UploadUrlRequest(BaseModel):
    filename: str
    mime_type: str
    asset_type: str
    file_size_bytes: int | None = None


class UploadUrlResponse(BaseModel):
    upload_url: str
    s3_key: str
    s3_bucket: str
    expires_in: int = 3600


class AssetCreate(BaseModel):
    s3_key: str
    s3_bucket: str
    filename: str
    mime_type: str
    asset_type: str
    device_type: str | None = None
    file_size_bytes: int | None = None
    width_px: int | None = None
    height_px: int | None = None
    sort_order: int = 0


class AssetResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    asset_type: str
    device_type: str | None
    filename: str
    mime_type: str
    file_size_bytes: int | None
    width_px: int | None
    height_px: int | None
    sort_order: int
    url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssetReorderRequest(BaseModel):
    asset_ids: list[uuid.UUID]
