import uuid
from datetime import datetime
from pydantic import BaseModel


class VideoResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    job_id: uuid.UUID
    target_store: str
    orientation: str
    resolution: str
    duration_seconds: float
    file_size_bytes: int | None
    cdn_url: str | None
    watermarked: bool
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoListResponse(BaseModel):
    items: list[VideoResponse]
