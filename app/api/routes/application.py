from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.application import Application
from app.models.job import Job
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationResponse


router = APIRouter(
    prefix="/api/applications",
    tags=["Applications"]
)


def build_application_response(application: Application) -> dict:
    return {
        "id": application.id,
        "job_id": application.job_id,
        "user_id": application.user_id,
        "status": application.status,
        "applied_at": application.applied_at,
        "notes": application.notes,
        "job_title": application.job.title,
        "company_name": application.job.company_name,
        "location": application.job.location,
    }


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = (
        db.query(Job)
        .filter(
            Job.id == application_data.job_id,
            Job.owner_id == current_user.id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    new_application = Application(
        job_id=application_data.job_id,
        user_id=current_user.id,
        status=application_data.status,
        notes=application_data.notes
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return build_application_response(new_application)


@router.get(
    "",
    response_model=list[ApplicationResponse]
)
def get_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    applications = (
        db.query(Application)
        .filter(Application.user_id == current_user.id)
        .order_by(Application.applied_at.desc())
        .all()
    )

    return [
        build_application_response(application)
        for application in applications
    ]


@router.get(
    "/{application_id}",
    response_model=ApplicationResponse
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id
        )
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return build_application_response(application)


@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse
)
def update_application(
    application_id: int,
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id
        )
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    application.status = application_data.status
    application.notes = application_data.notes

    db.commit()
    db.refresh(application)

    return build_application_response(application)


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id
        )
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    db.delete(application)
    db.commit()

    return None
