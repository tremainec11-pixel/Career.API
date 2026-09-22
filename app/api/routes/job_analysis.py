from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.job import Job
from app.models.job_analysis import JobAnalysis
from app.models.user import User
from app.schemas.job_analysis import (
    JobAnalysisCreate,
    JobAnalysisResponse
)
from app.services.ai_service import analyze_job_description


router = APIRouter(
    prefix="/api/jobs",
    tags=["Job Analysis"]
)


@router.post(
    "/{job_id}/analysis",
    response_model=JobAnalysisResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job_analysis(
    job_id: int,
    analysis_data: JobAnalysisCreate,
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

    existing_analysis = (
        db.query(JobAnalysis)
        .filter(JobAnalysis.job_id == job_id)
        .first()
    )

    if existing_analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job analysis already exists"
        )

    new_analysis = JobAnalysis(
        job_id=job.id,
        summary=analysis_data.summary,
        required_skills=analysis_data.required_skills,
        responsibilities=analysis_data.responsibilities,
        keywords=analysis_data.keywords,
        seniority=analysis_data.seniority
    )

    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return new_analysis


@router.post(
    "/{job_id}/analysis/ai",
    response_model=JobAnalysisResponse,
    status_code=status.HTTP_200_OK
)
def analyze_job_with_ai(
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

    ai_result = analyze_job_description(
        job.description
    )

    existing_analysis = (
        db.query(JobAnalysis)
        .filter(JobAnalysis.job_id == job_id)
        .first()
    )

    if existing_analysis:
        existing_analysis.summary = ai_result["summary"]
        existing_analysis.required_skills = ai_result["required_skills"]
        existing_analysis.responsibilities = ai_result["responsibilities"]
        existing_analysis.keywords = ai_result["keywords"]
        existing_analysis.seniority = ai_result["seniority"]

        db.commit()
        db.refresh(existing_analysis)

        return existing_analysis

    new_analysis = JobAnalysis(
        job_id=job.id,
        summary=ai_result["summary"],
        required_skills=ai_result["required_skills"],
        responsibilities=ai_result["responsibilities"],
        keywords=ai_result["keywords"],
        seniority=ai_result["seniority"]
    )

    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)

    return new_analysis


@router.get(
    "/{job_id}/analysis",
    response_model=JobAnalysisResponse
)
def get_job_analysis(
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

    analysis = (
        db.query(JobAnalysis)
        .filter(JobAnalysis.job_id == job_id)
        .first()
    )

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job analysis not found"
        )

    return analysis