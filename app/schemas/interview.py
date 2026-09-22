from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InterviewCreate(BaseModel):
    application_id: int
    interview_date: datetime
    interview_type: str = "Video"
    status: str = "Scheduled"
    notes: str | None = None


class InterviewResponse(BaseModel):
    id: int
    application_id: int
    user_id: int
    interview_date: datetime
    interview_type: str
    status: str
    notes: str | None

    job_title: str
    company_name: str

    model_config = ConfigDict(from_attributes=True)
