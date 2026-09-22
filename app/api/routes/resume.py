from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.services.pdf_service import extract_text_from_pdf


router = APIRouter(
    prefix="/api/resumes",
    tags=["Resumes"]
)


@router.get(
    "",
    response_model=list[ResumeResponse]
)
def get_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.id.desc())
        .all()
    )


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse
)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    return resume


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty"
        )

    extracted_text = extract_text_from_pdf(file_content)

    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from the PDF"
        )

    new_resume = Resume(
        user_id=current_user.id,
        file_name=file.filename or "resume.pdf",
        file_path=None,
        extracted_text=extracted_text
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return new_resume


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    db.delete(resume)
    db.commit()

    return None
