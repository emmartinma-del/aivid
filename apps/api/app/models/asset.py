from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.project import Project

class AssetType:
    SCREENSHOT_IPHONE = "screenshot_iphone"
    SCREENSHOT_IPAD = "screenshot_ipad"
    SCREENSHOT_ANDROID = "screenshot_android"
    ICON = "icon"
    GAMEPLAY_CLIP = "gameplay_clip"


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)
    device_type: Mapped[str | None] = mapped_column(String(50))  # iphone_67, iphone_65, ipad_129, etc.
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    s3_bucket: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    width_px: Mapped[int | None] = mapped_column(Integer)
    height_px: Mapped[int | None] = mapped_column(Integer)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="assets")
