
import os
import json
import re
import asyncio
import logging
import hashlib
import time

import pymupdf
from dotenv import load_dotenv
from google import genai
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from backend/.env")

client = genai.Client(api_key=api_key)

# Keep the existing Gemini model
MODEL_NAME = "gemini-3.5-flash"

# Limit simultaneous Gemini requests
gemini_semaphore = asyncio.Semaphore(2)


# --------------------------------------------------
# 2. CACHE CONFIGURATION
# --------------------------------------------------

resume_analysis_cache = {}

CACHE_TTL = 3600       # 1 hour
MAX_CACHE_SIZE = 100


def generate_cache_key(feature, *inputs):
    """Generate a unique cache key for each feature and its inputs."""

    cache_data = json.dumps(
        [feature, *inputs],
        ensure_ascii=False,
        sort_keys=True
    )

    return hashlib.sha256(
        cache_data.encode("utf-8")
    ).hexdigest()


def get_cached_analysis(cache_key):
    """Return cached result if it exists and is not expired."""

    cached = resume_analysis_cache.get(cache_key)

    if cached is None:
        return None

    if time.time() - cached["timestamp"] > CACHE_TTL:
        del resume_analysis_cache[cache_key]
        logger.info("Expired cache entry removed")
        return None

    logger.info("Cache hit")
    return cached["analysis"]


def save_cached_analysis(cache_key, analysis):
    """Save result and remove expired entries."""

    current_time = time.time()

    # Remove expired entries
    expired_keys = [
        key
        for key, value in resume_analysis_cache.items()
        if current_time - value["timestamp"] > CACHE_TTL
    ]

    for key in expired_keys:
        del resume_analysis_cache[key]

    # Remove oldest entry if cache is full
    if (
        cache_key not in resume_analysis_cache
        and len(resume_analysis_cache) >= MAX_CACHE_SIZE
    ):
        oldest_key = min(
            resume_analysis_cache,
            key=lambda key: resume_analysis_cache[key]["timestamp"]
        )

        del resume_analysis_cache[oldest_key]

    resume_analysis_cache[cache_key] = {
        "analysis": analysis,
        "timestamp": current_time
    }

    logger.info("Result saved to cache")


# --------------------------------------------------
# 3. INITIALIZE FASTAPI
# --------------------------------------------------

app = FastAPI(
    title="AI Resume Interview Assistant",
    description="AI-powered Resume Analysis API",
    version="2.0.0"
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


# --------------------------------------------------
# 4. HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
async def home():

    return {
        "message": "AI Resume Assistant API is running",
        "status": "success"
    }


# --------------------------------------------------
# 5. PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_resume_text(contents: bytes):

    try:

        with pymupdf.open(
            stream=contents,
            filetype="pdf"
        ) as pdf_document:

            resume_text = "\n".join(
                page.get_text()
                for page in pdf_document
            )

        if not resume_text.strip():

            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF. It may be scanned."
            )

        return resume_text

    except HTTPException:
        raise

    except Exception:

        logger.exception("PDF extraction failed")

        raise HTTPException(
            status_code=400,
            detail="PDF processing failed. Please check the uploaded file."
        )


# --------------------------------------------------
# 6. GEMINI JSON GENERATION
# --------------------------------------------------

def clean_json_response(response_text):

    if not response_text:
        raise ValueError("Gemini returned an empty response")

    text = response_text.strip()

    # Remove Markdown code fences
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r"\s*```$", "", text)

    result = json.loads(text)

    if not isinstance(result, dict):
        raise ValueError("Gemini response must be a JSON object")

    return result


def call_gemini(prompt):

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return clean_json_response(response.text)


async def generate_ai_json(prompt):

    async with gemini_semaphore:

        for attempt in range(3):

            try:

                logger.info(
                    "Sending Gemini request. Attempt %s/3",
                    attempt + 1
                )

                result = await asyncio.to_thread(
                    call_gemini,
                    prompt
                )

                logger.info("Gemini response received successfully")

                return result

            except Exception as error:

                error_message = str(error).upper()

                # Quota or rate-limit errors
                if (
                    "429" in error_message
                    or "RESOURCE_EXHAUSTED" in error_message
                ):

                    logger.warning(
                        "Gemini quota exhausted. No application retry will be attempted."
                    )

                    raise HTTPException(
                        status_code=429,
                        detail=(
                            "Gemini API quota or rate limit reached. "
                            "Please check Google AI Studio usage and try again "
                            "after your quota resets."
                        )
                    )

                # Temporary server errors
                temporary_error = any(
                    term in error_message
                    for term in [
                        "503",
                        "UNAVAILABLE",
                        "504",
                        "DEADLINE_EXCEEDED",
                        "INTERNAL SERVER ERROR"
                    ]
                )

                if temporary_error and attempt < 2:

                    wait_time = 2 ** (attempt + 1)

                    logger.warning(
                        "Temporary Gemini error. Retrying in %s seconds",
                        wait_time
                    )

                    await asyncio.sleep(wait_time)

                    continue

                if temporary_error:

                    raise HTTPException(
                        status_code=503,
                        detail=(
                            "Gemini is temporarily unavailable "
                            "after multiple attempts. Please try again later."
                        )
                    )

                logger.exception("Unexpected Gemini request failure")

                raise HTTPException(
                    status_code=502,
                    detail=(
                        "Gemini request failed. Check API configuration "
                        "and backend logs."
                    )
                )

        raise HTTPException(
            status_code=503,
            detail="Gemini request could not be completed."
        )


# --------------------------------------------------
# 7. COMMON PDF VALIDATION
# --------------------------------------------------

async def get_resume_text(file: UploadFile):

    if not file.filename or not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file"
        )

    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty"
        )

    return extract_resume_text(contents)


# --------------------------------------------------
# 8. UPLOAD RESUME ENDPOINT
# --------------------------------------------------

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    resume_text = await get_resume_text(file)

    return {
        "filename": file.filename,
        "total_characters": len(resume_text),
        "resume_text": resume_text
    }


# --------------------------------------------------
# 9. RESUME ANALYSIS ENDPOINT
# --------------------------------------------------

@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...)):

    logger.info("Resume analysis request received")

    resume_text = await get_resume_text(file)

    cache_key = generate_cache_key(
        "resume-analysis",
        resume_text
    )

    # Check cache
    cached_analysis = get_cached_analysis(cache_key)

    if cached_analysis is not None:

        logger.info("Resume analysis cache hit")

        return {
            "filename": file.filename,
            "analysis": cached_analysis
        }

    logger.info("Resume analysis cache miss. Calling Gemini.")

    prompt = f"""
You are an expert technical recruiter and resume analyzer.

Analyze the following resume carefully.

Return a valid JSON object with exactly these fields:

{{
    "candidate_name": "",
    "professional_summary": "",
    "technical_skills": [],
    "programming_languages": [],
    "tools_and_frameworks": [],
    "education": [],
    "projects": [],
    "experience": [],
    "certifications": [],
    "strengths": [],
    "areas_to_improve": []
}}

Instructions:
1. Extract only information present in the resume.
2. Do not invent skills, experience, or achievements.
3. Keep the summary concise and professional.
4. Identify technical skills accurately.
5. Summarize projects with technologies and objectives.
6. Identify missing or weak resume details.
7. Return valid JSON only.
8. Do not include Markdown code fences.

RESUME:

{resume_text}
"""

    analysis = await generate_ai_json(prompt)

    save_cached_analysis(cache_key, analysis)

    logger.info("Resume analysis saved to cache")

    return {
        "filename": file.filename,
        "analysis": analysis
    }


# --------------------------------------------------
# 10. JOB DESCRIPTION MATCHING ENDPOINT
# --------------------------------------------------

@app.post("/match-job")
async def match_job(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):

    logger.info("Job matching request received")

    if not job_description.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )

    resume_text = await get_resume_text(file)

    normalized_job_description = " ".join(
        job_description.split()
    )

    cache_key = generate_cache_key(
        "job-matching",
        resume_text,
        normalized_job_description
    )

    # Check cache
    cached_result = get_cached_analysis(cache_key)

    if cached_result is not None:

        logger.info("Job matching cache hit")

        return {
            "filename": file.filename,
            **cached_result
        }

    logger.info("Job matching cache miss. Calling Gemini.")

    prompt = f"""
You are an expert technical recruiter.

Compare the candidate's resume with the job description.

Return a valid JSON object with these exact fields:

{{
    "match_score": 0,
    "overall_assessment": "",
    "matching_skills": [],
    "missing_skills": [],
    "partially_matching_skills": [],
    "relevant_projects": [],
    "strengths": [],
    "recommendations": [],
    "learning_suggestions": []
}}

Instructions:

1. Calculate match_score as an estimated percentage
   between 0 and 100 based on demonstrated alignment.

2. Compare required skills with skills actually shown
   in the resume.

3. Do not assume the candidate knows a skill unless
   the resume supports it.

4. Identify matching and missing technical skills.

5. Identify relevant projects from the resume.

6. Give practical recommendations to improve the resume.

7. Suggest useful topics to learn for the role.

8. Do not invent work experience or achievements.

9. Return valid JSON only, without Markdown fences.

RESUME:

{resume_text}

JOB DESCRIPTION:

{normalized_job_description}
"""

    analysis = await generate_ai_json(prompt)

    score = analysis.get("match_score")

    if (
        not isinstance(score, (int, float))
        or isinstance(score, bool)
        or not 0 <= score <= 100
    ):

        raise HTTPException(
            status_code=502,
            detail="Gemini returned an invalid job match score"
        )

    # Save successful result
    save_cached_analysis(cache_key, analysis)

    logger.info("Job matching result saved to cache")

    return {
        "filename": file.filename,
        **analysis
    }


# --------------------------------------------------
# 11. INTERVIEW QUESTION GENERATOR
# --------------------------------------------------

@app.post("/generate-questions")
async def generate_questions(
    file: UploadFile = File(...),
    job_role: str = Form(...)
):

    logger.info("Interview question generation request received")

    if not job_role.strip():

        raise HTTPException(
            status_code=400,
            detail="Please enter a job role"
        )

    resume_text = await get_resume_text(file)

    normalized_job_role = " ".join(
        job_role.split()
    ).lower()

    cache_key = generate_cache_key(
        "interview-preparation",
        resume_text,
        normalized_job_role
    )

    # Check cache
    cached_questions = get_cached_analysis(cache_key)

    if cached_questions is not None:

        logger.info("Interview questions cache hit")

        return {
            "filename": file.filename,
            **cached_questions
        }

    logger.info("Interview questions cache miss. Calling Gemini.")

    prompt = f"""
You are an experienced technical interviewer.

Generate 20 personalized interview questions
based on the candidate's resume and target job role.

TARGET JOB ROLE:

{job_role}

CANDIDATE RESUME:

{resume_text}

Return a valid JSON object with exactly these fields:

{{
    "job_role": "",
    "python_questions": [
        {{
            "question": "",
            "suggested_answer": "",
            "explanation": ""
        }}
    ],
    "sql_questions": [
        {{
            "question": "",
            "suggested_answer": "",
            "explanation": ""
        }}
    ],
    "project_questions": [
        {{
            "question": "",
            "suggested_answer": "",
            "explanation": ""
        }}
    ],
    "hr_questions": [
        {{
            "question": "",
            "suggested_answer": "",
            "explanation": ""
        }}
    ]
}}

Instructions:

1. Generate exactly 5 questions in each category.
2. Make questions relevant to the target job role.
3. Personalize project questions using actual resume projects.
4. Do not invent candidate experience or achievements.
5. Provide clear, beginner-friendly suggested answers.
6. Include a short explanation for each answer.
7. Make HR answers suggestions, not fabricated personal facts.
8. Return valid JSON only.
9. Do not include Markdown code fences.
"""

    questions = await generate_ai_json(prompt)

    categories = [
        "python_questions",
        "sql_questions",
        "project_questions",
        "hr_questions"
    ]

    # Validate question categories and counts
    for category in categories:

        category_questions = questions.get(category)

        if (
            not isinstance(category_questions, list)
            or len(category_questions) != 5
        ):

            raise HTTPException(
                status_code=502,
                detail=f"Gemini returned an invalid {category} list"
            )

        for item in category_questions:

            if (
                not isinstance(item, dict)
                or not item.get("question")
            ):

                raise HTTPException(
                    status_code=502,
                    detail=f"Invalid question format in {category}"
                )

    # Save successful questions
    save_cached_analysis(cache_key, questions)

    logger.info("Interview questions saved to cache")

    return {
        "filename": file.filename,
        **questions
    }


# --------------------------------------------------
# 12. APPLICATION STATUS
# --------------------------------------------------

@app.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "backend": "running",
        "gemini_model": MODEL_NAME,
        "cache_entries": len(resume_analysis_cache)
    }
