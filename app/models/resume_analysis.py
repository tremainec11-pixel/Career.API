from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id"),
        nullable=False,
        unique=True,
        index=True
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    skills: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    experience: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    education: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    certifications: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    keywords: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    resume = relationship("Resume")