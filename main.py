from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.application import router as application_router
from app.api.routes.interview import router as interview_router
from app.api.routes.job import router as job_router
from app.api.routes.job_analysis import router as job_analysis_router
from app.api.routes.resume import router as resume_router
from app.api.routes.resume_analysis import router as resume_analysis_router
from app.core.dependencies import get_current_user
from app.models.user import User


app = FastAPI(
    title="CareerAI API",
    description="AI-powered career and job intelligence platform",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(application_router)
app.include_router(interview_router)
app.include_router(job_router)
app.include_router(job_analysis_router)
app.include_router(resume_router)
app.include_router(resume_analysis_router)


@app.get("/")
def root():
    return {
        "message": "CareerAI API is running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/api/auth/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name
    }