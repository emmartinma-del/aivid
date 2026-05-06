from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.project import Project


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    organization_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    role: Mapped[str] = mapped_column(String(50), default="owner")  # owner, admin, member
    is_active: Mapped[bool] = mapped_column(default=True)

    organization: Mapped["Organization | None"] = relationship(back_populates="users")
    projects: Mapped[list["Project"]] = relationship(back_populates="created_by_user")
