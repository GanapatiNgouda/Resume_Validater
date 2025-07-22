"""
Job Description Upload & Processing Endpoint
- Accepts PDF/DOCX uploads
- Extracts text
- Calls Gemini API for key detail extraction
- Stores results in SQL Server
"""

from database import execute_non_query
from google import genai
from google.genai.types import GenerateContentConfig
import os
import uuid
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel
import pdfplumber
from config import settings

# PDF & DOCX extraction
from pypdf import PdfReader
from docx import Document

# Gemini API (placeholder)
import requests

router = APIRouter()

UPLOAD_DIR = "resume_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class res(BaseModel):
    question: str
    answer: str


class resume(BaseModel):
    id: int | None = None
    name: str
    location: str
    education: List[str] = []
    skills: List[str] = []
    email: str
    phone: str
    experience: List[str] = []
    worked_company: str
    experience_year:int
    github_link: str
    linkedin_link: str


# Helper: Extract text from PDF
def extract_pdf_text(file_path):
    try:
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {str(e)}")


# Helper: Extract text from DOCX
def extract_docx_text(file_path):
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DOCX extraction failed: {str(e)}")


def call_gemini_api(resume_text: str):
    # Placeholder: Replace with actual Gemini API endpoint and key

    context = f"""
Extract the following details from this resume text. Respond ONLY with a valid JSON object matching this schema:
{{
  'name': str,
  'location': str,
  'education': list,
  'skills': list,
  'email': str,
  'phone': list,
   'experience' :List,
   'worked_company' : str,
   'experience_year':int,
    'github_link' :str,
    'linkedin_link' :str
    
  
}}

"""
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not set in environment variables.",
            )

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=GenerateContentConfig(
                system_instruction=["answer should based on given context ", context],
                response_mime_type="application/json",
                response_json_schema=resume.model_json_schema(),
            ),
            contents=resume_text,
        )
        generated_answer = parse_response(response)
        return generated_answer
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")


# Helper: Insert JD into SQL Server
def insert_resume(rs: resume):

    query = """
    INSERT INTO resume_checker  (
        name,location,education ,skills,email,phone,experience,worked_company,experience_year,github_link,linkedin_link
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        rs.name,
        rs.location,
        json.dumps(rs.education),
        json.dumps(rs.skills),
        rs.email,
        rs.phone,
        json.dumps(rs.experience),
        rs.worked_company,
        rs.experience_year,
        rs.github_link,
        rs.linkedin_link,
    )
    try:
        execute_non_query(query, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert error: {str(e)}")


@router.post("/upload-resume", response_model=resume, status_code=201)
def upload_resume(file: UploadFile = File(...)):
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400, detail="Unsupported file type. Only PDF and DOCX allowed."
        )

    # Save file with unique name
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")

    # Extract text
    if ext == ".pdf":
        resume_text = extract_pdf_text(file_path)
    else:
        resume_text = extract_docx_text(file_path)
    if not resume_text:
        raise HTTPException(status_code=400, detail="No text extracted from file.")

    # Call Gemini API
    ai_data = call_gemini_api(resume_text)
    if not ai_data.get("name"):
        raise HTTPException(
            status_code=422, detail="AI did not return required job details."
        )

    # Build JD object
    rs = resume(**ai_data, jd_file_path=file_path)

    # Insert into DB
    insert_resume(rs)

    return rs


@router.post("/resume_detials/")
async def resume_detials(resume: UploadFile,):
    # ... file processing logic ...
    with pdfplumber.open(resume.file) as pdf:
        pages = pdf.pages
        resume_text = ""

        for page in pages:
            resume_text += page.extract_text()

    try:
        # Initialize the Gemini client with the API key from environment variables
        # Ensure GEMINI_API_KEY is set in your environment
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not set in environment variables.",
            )

        client = genai.Client(api_key=api_key)

        context = "I have given resume i need all details in resume"

        prompt = f"""
        
        ---
        Resume:
        {resume_text}
        ---

        
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=GenerateContentConfig(
                system_instruction=[context],
                response_mime_type="application/json",
                # esponse_json_schema=Qa.model_json_schema()
            ),
            contents=[prompt],
        )
        return parse_response(response)
    except Exception as e:
        # Handle any exceptions during the process
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


def parse_response(response):
    if response.parsed is None:
        try:
            # Attempt to parse the raw text as JSON
            parsed_data = json.loads(response.text)
            return parsed_data
        except json.JSONDecodeError as json_e:
            # If manual parsing fails, it means the model returned invalid JSON
            print(f"Manual JSON parsing failed: {json_e}")
            raise HTTPException(
                status_code=500,
                detail=f"Model response could not be parsed as JSON. Raw text: '{response.text}'. Error: {json_e}",
            )
    else:
        # If response.parsed is not None, return it directly
        return response.parsed


@router.get("/resumes", response_model=List[resume])
def get_all_resumes():
    """Get all resume details from the database."""
    query = "SELECT id,name, location, education, skills, email, phone, experience, worked_company, experience_year, github_link, linkedin_link FROM resume_checker"
    try:
        from database import execute_query
        rows = execute_query(query)
        resumes = []
        for row in rows:
            resumes.append(resume(
                id=row[0],
                name=row[1],
                location=row[2],
                education=json.loads(row[3]) if row[3] else [],
                skills=json.loads(row[4]) if row[4] else [],
                email=row[5],
                phone=row[6],
                experience=json.loads(row[7]) if row[7] else [],
                worked_company=row[8],
                experience_year=row[9],
                github_link=row[10],
                linkedin_link=row[11],
            ))
        return resumes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
