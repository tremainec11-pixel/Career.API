from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobCreate, JobResponse


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_job = Job(
        title=job_data.title,
        company_name=job_data.company_name,
        location=job_data.location,
        description=job_data.description,
        url=job_data.url,
        owner_id=current_user.id
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@router.get(
    "",
    response_model=list[JobResponse]
)
def get_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    jobs = (
        db.query(Job)
        .filter(Job.owner_id == current_user.id)
        .order_by(Job.created_at.desc())
        .all()
    )

    return jobs


@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.owner_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job