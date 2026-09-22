from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.models.user import User
from app.services.ai_service import analyze_resume
from app.schemas.resume import ResumeAnalysisResponse


router = APIRouter(
    prefix="/api/resumes",
    tags=["Resume Analysis"]
)


@router.post(
    "/{resume_id}/analysis/ai",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_200_OK
)
def analyze_resume_with_ai(
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

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    if not resume.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume does not contain extracted text"
        )

    ai_result = analyze_resume(
        resume.extracted_text
    )

    existing_analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.resume_id == resume_id
        )
        .first()
    )

    if existing_analysis:
        existing_analysis.summary = ai_result["summary"]
        existing_analysis.skills = ai_result["skills"]
        existing_analysis.experience = ai_result["experience"]
        existing_analysis.education = ai_result["education"]
        existing_analysis.certifications = ai_result["certifications"]
        existing_analysis.keywords = ai_result["keywords"]

        db.commit()
        db.refresh(existing_analysis)

        return {
            "id": existing_analysis.id,
            "resume_id": existing_analysis.resume_id,
            "summary": existing_analysis.summary,
            "skills": existing_analysis.skills,
            "experience": existing_analysis.experience,
            "education": existing_analysis.education,
            "certifications": existing_analysis.certifications,
            "keywords": existing_analysis.keywords
        }

    new_analysis = ResumeAnalysis(
        resume_id=resume.id,
        summary=ai_result["summary"],
        skills=ai_result["skills"],
        experience=ai_result["experience"],
        education=ai_result["education"],
        certifications=ai_result["certifications"],
        keywords=ai_result["keywords"]
    )

    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return {
        "id": new_analysis.id,
        "resume_id": new_analysis.resume_id,
        "summary": new_analysis.summary,
        "skills": new_analysis.skills,
        "experience": new_analysis.experience,
        "education": new_analysis.education,
        "certifications": new_analysis.certifications,
        "keywords": new_analysis.keywords
    }
