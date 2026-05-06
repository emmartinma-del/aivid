import uuid
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import mapped_column, Mapped
from app.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


def uuid_pk():
    return mapped_column(default=uuid.uuid4, primary_key=True)
