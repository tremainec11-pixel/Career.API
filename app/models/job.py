from datetime import datetime

from sqlalchemy import DateTime, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    company_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    location: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    owner = relationship("User")