from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Applied",
        nullable=False
    )

    applied_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    job = relationship("Job")
    user = relationship("User")