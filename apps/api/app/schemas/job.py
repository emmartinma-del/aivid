import uuid
from datetime import datetime
from pydantic import BaseModel


class JobResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    current_step: str | None
    progress_pct: int
    error_message: str | None
    retry_count: int
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
