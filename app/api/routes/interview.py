from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.application import Application
from app.models.interview import Interview
from app.models.user import User
from app.schemas.interview import InterviewCreate, InterviewResponse


router = APIRouter(
    prefix="/api/interviews",
    tags=["Interviews"]
)


def build_interview_response(interview: Interview):
    return {
        "id": interview.id,
        "application_id": interview.application_id,
        "user_id": interview.user_id,
        "interview_date": interview.interview_date,
        "interview_type": interview.interview_type,
        "status": interview.status,
        "notes": interview.notes,
        "job_title": interview.application.job.title,
        "company_name": interview.application.job.company_name,
    }


@router.post(
    "",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED
)
def create_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = (
        db.query(Application)
        .filter(
            Application.id == interview_data.application_id,
            Application.user_id == current_user.id
        )
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    new_interview = Interview(
        application_id=interview_data.application_id,
        user_id=current_user.id,
        interview_date=interview_data.interview_date,
        interview_type=interview_data.interview_type,
        status=interview_data.status,
        notes=interview_data.notes
    )

    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)

    return build_interview_response(new_interview)


@router.get(
    "",
    response_model=list[InterviewResponse]
)
def get_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == current_user.id)
        .order_by(Interview.interview_date.asc())
        .all()
    )

    return [
        build_interview_response(interview)
        for interview in interviews
    ]


@router.get(
    "/{interview_id}",
    response_model=InterviewResponse
)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = (
        db.query(Interview)
        .filter(
            Interview.id == interview_id,
            Interview.user_id == current_user.id
        )
        .first()
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    return build_interview_response(interview)


@router.patch(
    "/{interview_id}",
    response_model=InterviewResponse
)
def update_interview(
    interview_id: int,
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = (
        db.query(Interview)
        .filter(
            Interview.id == interview_id,
            Interview.user_id == current_user.id
        )
        .first()
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    interview.interview_date = interview_data.interview_date
    interview.interview_type = interview_data.interview_type
    interview.status = interview_data.status
    interview.notes = interview_data.notes

    db.commit()
    db.refresh(interview)

    return build_interview_response(interview)


@router.delete(
    "/{interview_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    interview = (
        db.query(Interview)
        .filter(
            Interview.id == interview_id,
            Interview.user_id == current_user.id
        )
        .first()
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    db.delete(interview)
    db.commit()

    return None
