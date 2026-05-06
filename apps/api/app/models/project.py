from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ARRAY, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization
    from app.models.asset import Asset
    from app.models.job import GenerationJob
    from app.models.video import Video

# Project statuses
class ProjectStatus:
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

# Style themes
class StyleTheme:
    MODERN = "modern"
    GAMING = "gaming"
    CORPORATE = "corporate"
    FUN = "fun"

# Target stores
class TargetStore:
    IOS = "ios"
    ANDROID = "android"
    BOTH = "both"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = uuid_pk()
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), nullable=False)
    app_description: Mapped[str | None] = mapped_column(Text)
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    app_category: Mapped[str | None] = mapped_column(String(100))
    target_store: Mapped[str] = mapped_column(String(50), default=TargetStore.IOS)
    style_theme: Mapped[str] = mapped_column(String(50), default=StyleTheme.MODERN)
    status: Mapped[str] = mapped_column(String(50), default=ProjectStatus.DRAFT, index=True)

    organization: Mapped["Organization"] = relationship(back_populates="projects")
    created_by_user: Mapped["User"] = relationship(back_populates="projects")
    assets: Mapped[list["Asset"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    jobs: Mapped[list["GenerationJob"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    videos: Mapped[list["Video"]] = relationship(back_populates="project", cascade="all, delete-orphan")
