from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    job_id: int
    status: str = "Applied"
    notes: str | None = None


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    status: str
    applied_at: datetime
    notes: str | None

    job_title: str
    company_name: str
    location: str | None

    model_config = ConfigDict(from_attributes=True)
