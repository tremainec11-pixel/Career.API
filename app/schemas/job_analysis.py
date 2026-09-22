from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobAnalysisCreate(BaseModel):
    summary: str
    required_skills: str
    responsibilities: str
    keywords: str
    seniority: str | None = None


class JobAnalysisResponse(BaseModel):
    id: int
    job_id: int
    summary: str
    required_skills: str
    responsibilities: str
    keywords: str
    seniority: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)