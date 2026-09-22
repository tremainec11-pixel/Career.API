from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_path: str | None
    extracted_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeAnalysisResponse(BaseModel):
    id: int
    resume_id: int
    summary: str
    skills: str
    experience: str
    education: str
    certifications: str
    keywords: str

    model_config = ConfigDict(from_attributes=True)