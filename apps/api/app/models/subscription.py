from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from app.models.organization import Organization

TIER_LIMITS = {
    "free": 1,
    "starter": 5,
    "pro": 20,
    "agency": 999999,
}


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = uuid_pk()
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), unique=True, nullable=False)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    stripe_price_id: Mapped[str | None] = mapped_column(String(255))
    tier: Mapped[str] = mapped_column(String(50), default="free")  # free, starter, pro, agency
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, canceled, past_due, trialing
    videos_used_this_period: Mapped[int] = mapped_column(Integer, default=0)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    organization: Mapped["Organization"] = relationship(back_populates="subscription")

    @property
    def videos_limit(self) -> int:
        return TIER_LIMITS.get(self.tier, 1)

    @property
    def has_quota(self) -> bool:
        return self.videos_used_this_period < self.videos_limit

    @property
    def is_active(self) -> bool:
        return self.status in ("active", "trialing")
