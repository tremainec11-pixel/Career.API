from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    interview_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    interview_type: Mapped[str] = mapped_column(
        String(50),
        default="Video",
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Scheduled",
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    application = relationship("Application")
    user = relationship("User")
