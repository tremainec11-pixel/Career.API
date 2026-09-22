import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel

from app.core.config import settings


class ResumeAnalysisResult(BaseModel):
    summary: str
    skills: list[str]
    experience: list[str]
    education: list[str]
    certifications: list[str]
    keywords: list[str]


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
            skills=[
                "C#",
                "JavaScript",
                "TypeScript",
                "SQL",
                "React",
                "Angular",
                "ASP.NET Core",
                "REST APIs",
                "SQL Server",
                "PostgreSQL",
                "MongoDB",
                "Docker"
            ],
            experience=[
                "Full Stack Developer experience developing e-commerce applications.",
                "Developed REST APIs and database-backed applications.",
                "Built modern web interfaces using Angular and React.",
                "Previous experience includes technical support.",
                "Previous experience includes sales."
            ],
            education=[
                "Industrial Engineering from Universidad Latinoamericana.",
                "Master's studies in Software Engineering at Universidad UTEL."
            ],
            certifications=[
                "Back-End Development with .NET",
                "Full-Stack Integration",
                "Security and Authentication",
                "Data Structures and Algorithms",
                "Deployment and DevOps"
            ],
            keywords=[
                "Full Stack Developer",
                "React",
                "Angular",
                "ASP.NET Core",
                ".NET",
                "REST APIs",
                "SQL",
                "PostgreSQL",
                "MongoDB",
                "Docker"
            ]
        )

        return result.model_dump()

    prompt = f"""
Analyze this resume and return ONLY valid JSON.

Return exactly these six fields:

{{
  "summary": "",
  "skills": [],
  "experience": [],
  "education": [],
  "certifications": [],
  "keywords": []
}}

RULES:

- summary: one short sentence.
- skills: maximum 12 items.
- experience: maximum 5 short items.
- Include ONLY actual jobs or professional work in experience.
- NEVER include universities, degrees, courses, or education in experience.
- education: maximum 3 short items.
- Include ONLY universities, degrees, fields of study, and academic dates.
- certifications: maximum 5 items.
- Include ONLY explicitly listed certifications, courses, training, or credentials.
- keywords: maximum 10 important employment-related keywords.
- Use ONLY information explicitly present in the resume.
- Do not invent information.
- Do not infer missing information.
- Return JSON only.
- Do not add extra fields.

RESUME:

{resume_text}
"""

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": "10m",
        "options": {
            "num_predict": 350
        }
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
        raise RuntimeError(
            "Ollama returned invalid JSON."
        ) from exc

    try:
        parsed_result.setdefault("summary", "Not specified")
        parsed_result.setdefault("skills", [])
        parsed_result.setdefault("experience", [])
        parsed_result.setdefault("education", [])
        parsed_result.setdefault("certifications", [])
        parsed_result.setdefault("keywords", [])

        result = ResumeAnalysisResult.model_validate(parsed_result)

    except Exception as exc:
        raise RuntimeError(
            f"Ollama returned an unexpected analysis format: {parsed_result}"
        ) from exc

    return result.model_dump()