import uuid
from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    app_name: str
    app_description: str | None = None
    keywords: list[str] | None = None
    app_category: str | None = None
    target_store: str = "ios"
    style_theme: str = "modern"


class ProjectUpdate(BaseModel):
    name: str | None = None
    app_name: str | None = None
    app_description: str | None = None
    keywords: list[str] | None = None
    app_category: str | None = None
    target_store: str | None = None
    style_theme: str | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by: uuid.UUID
    name: str
    app_name: str
    app_description: str | None
    keywords: list[str] | None
    app_category: str | None
    target_store: str
    style_theme: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int
