import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel

from app.core.config import settings


class ResumeAnalysisResult(BaseModel):
    summary: str
    skills: str
    experience: str
    education: str
    certifications: str
    keywords: str


def analyze_job_description(job_description: str) -> dict:
    return {
        "summary": (
            "Full Stack Developer position focused on developing and "
            "maintaining web applications."
        ),
        "required_skills": (
            "React, Angular, C#, .NET, ASP.NET Core, SQL, REST APIs"
        ),
        "responsibilities": (
            "Develop and maintain web applications, build REST APIs, "
            "work with databases, and collaborate on software development tasks."
        ),
        "keywords": (
            "Full Stack Developer, React, Angular, .NET, ASP.NET Core, "
            "SQL, REST APIs"
        ),
        "seniority": "Mid-Level"
    }


def analyze_resume(resume_text: str) -> dict:

    if settings.ai_mock_mode:
        result = ResumeAnalysisResult(
            summary=(
                "Full Stack Developer with experience building web applications "
                "using React, Angular, ASP.NET Core, REST APIs, SQL, and PostgreSQL."
            ),
            skills=(
                "C#, JavaScript, TypeScript, SQL, React, Angular, ASP.NET Core, "
                "REST APIs, SQL Server, PostgreSQL, MongoDB, Docker, Git, GitHub, "
                "Entity Framework Core"
            ),
            experience=(
                "Full Stack Developer experience developing e-commerce applications, "
                "REST APIs, database-backed applications, and modern web interfaces. "
                "Previous experience includes technical support and sales."
            ),
            education=(
                "Industrial Engineering from Universidad Latinoamericana and "
                "Master's studies in Software Engineering at Universidad UTEL."
            ),
            certifications=(
                "Back-End Development with .NET, Full-Stack Integration, "
                "Security and Authentication, Data Structures and Algorithms, "
                "Deployment and DevOps."
            ),
            keywords=(
                "Full Stack Developer, React, Angular, ASP.NET Core, .NET, "
                "REST APIs, SQL, PostgreSQL, MongoDB, Docker, Git, GitHub"
            )
        )
        return result.model_dump()

    prompt = f"""
You are an expert professional resume parser and ATS analysis system.

Analyze the resume below and return ONLY valid JSON.

Return exactly these six fields:

{{
  "summary": "",
  "skills": "",
  "experience": "",
  "education": "",
  "certifications": "",
  "keywords": ""
}}

EXPERIENCE:
Include ONLY actual professional work experience.

Include job title, company, dates, responsibilities, and achievements
when explicitly available.

Do NOT include universities, degrees, academic programs, grades,
courses, or certifications in experience.

EDUCATION:
Include ONLY formal academic education.

Include university, degree, field of study, dates, and academic
information when explicitly available.

Do NOT include jobs, employers, responsibilities, or work experience
in education.

CERTIFICATIONS:
Include ONLY explicitly listed certifications, professional
certificates, completed courses, training programs, or credentials.

Do not turn ordinary skills into certifications.

SKILLS:
Include technical and professional skills explicitly found
in the resume.

KEYWORDS:
Include important employment-related keywords explicitly found
in the resume, especially job titles, technologies, programming
languages, frameworks, databases, tools, methodologies, and
professional areas.

STRICT RULES:

1. Return JSON only.
2. Do not use Markdown.
3. Do not add extra fields.
4. Do not invent information.
5. Do not infer missing information.
6. Use only information explicitly present in the resume.
7. Keep experience and education completely separate.
8. Keep certifications and ordinary skills completely separate.
9. If a category has no information, return "Not specified".
10. Preserve company names, job titles, dates, degrees, and
    certification names when available.
11. Do not combine unrelated jobs into one invented position.
12. Do not treat university projects as employment unless the
    resume explicitly identifies them as professional work.
13. Do not treat courses as university degrees.
14. Do not treat technologies as certifications.
15. Keep the output concise but informative.

RESUME:

{resume_text}
"""

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    request = Request(
        f"{settings.ollama_url}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(request, timeout=300) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Ollama request failed ({exc.code}): {error_body}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running on http://127.0.0.1:11434."
        ) from exc
    except TimeoutError as exc:
        raise RuntimeError(
            "Ollama analysis timed out after 300 seconds."
        ) from exc

    raw_result = response_data.get("response")

    if not raw_result:
        raise RuntimeError("Ollama returned an empty response.")

    try:
        parsed_result = json.loads(raw_result)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Ollama returned invalid JSON.") from exc

    try:
        parsed_result.setdefault("keywords", "Not specified")
        result = ResumeAnalysisResult.model_validate(parsed_result)
    except Exception as exc:
        raise RuntimeError(
            f"Ollama returned an unexpected analysis format: {parsed_result}"
        ) from exc

    return result.model_dump()
