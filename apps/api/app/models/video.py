from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, BigInteger, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.job import GenerationJob


class Video(Base, TimestampMixin):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("generation_jobs.id"), nullable=False)
    target_store: Mapped[str] = mapped_column(String(50), nullable=False)  # ios, android
    orientation: Mapped[str] = mapped_column(String(50), nullable=False)   # portrait, landscape
    resolution: Mapped[str] = mapped_column(String(50), nullable=False)    # e.g. 1080x1920
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    s3_bucket: Mapped[str] = mapped_column(String(255), nullable=False)
    cdn_url: Mapped[str | None] = mapped_column(String(1000))
    watermarked: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_script: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped["Project"] = relationship(back_populates="videos")
    job: Mapped["GenerationJob"] = relationship(back_populates="videos")
