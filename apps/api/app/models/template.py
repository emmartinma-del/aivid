from __future__ import annotations
import uuid
from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.base import TimestampMixin, uuid_pk


class Template(Base, TimestampMixin):
    __tablename__ = "templates"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    style_theme: Mapped[str] = mapped_column(String(50), nullable=False)
    target_store: Mapped[str] = mapped_column(String(50), nullable=False)
    orientation: Mapped[str] = mapped_column(String(50), nullable=False)
    ffmpeg_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    preview_url: Mapped[str | None] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
