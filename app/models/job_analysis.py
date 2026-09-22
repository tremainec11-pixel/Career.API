from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class JobAnalysis(Base):
    __tablename__ = "job_analyses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
        unique=True
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    required_skills: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    responsibilities: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    keywords: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    seniority: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    job = relationship("Job")