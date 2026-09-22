from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str
    company_name: str
    location: str | None = None
    description: str
    url: str | None = None


class JobResponse(BaseModel):
    id: int
    title: str
    company_name: str
    location: str | None
    description: str
    url: str | None
    created_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True)