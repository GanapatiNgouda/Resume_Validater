"""
Job Description Upload & Processing Endpoint
- Accepts PDF/DOCX uploads
- Extracts text
- Calls Gemini API for key detail extraction
- Stores results in SQL Server
"""
from google import genai
from google.genai.types import GenerateContentConfig
import os
import uuid
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel
from database import execute_non_query
from config import settings
import pdfplumber

# PDF & DOCX extraction
from pypdf import PdfReader
from docx import Document

# Gemini API (placeholder)
import requests

router = APIRouter()

UPLOAD_DIR = "jd_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class JobDescription(BaseModel):
    job_title: str
    company_name: str = None
    location: str = None
    experience_required: str = None
    qualifications: List[str] = []
    responsibilities: List[str] = []
    employment_type: str = None
    primary_skills: List[str] = []
    secondary_skills: List[str] = []
    tertiary_skills: List[str] = []
    jd_file_path: str = None

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

# Helper: Call Gemini API
    
os.environ["GEMINI_API_KEY"] = "AIzaSyDAOcP7uNLrb2F_0w8MpXIK8OeXoi-pwfo"


def call_gemini_api(jd_text: str):
    # Placeholder: Replace with actual Gemini API endpoint and key
    
    context =f"""
Extract the following details from this job description text. Respond ONLY with a valid JSON object matching this schema:
{{
  'job_title': str,
  'company_name': str,
  'location': str,
  'experience_required': str,
  'qualifications': list,
  'responsibilities': list,
  'employment_type': str,
  'primary_skills': list,
  'secondary_skills': list,
  'tertiary_skills': list
}}

"""
   
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set in environment variables.")

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=GenerateContentConfig(
                system_instruction=["answer should based on given context ", context],
                response_mime_type="application/json",
               response_json_schema=JobDescription.model_json_schema()
            ),
            contents=jd_text,
        )
        generated_answer = parse_response(response)
        return generated_answer
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")
    
    



# Helper: Insert JD into SQL Server
def insert_job_description(jd: JobDescription):
    query = """
    INSERT INTO job_descriptions (
        job_title, company_name, location, experience_required,
        qualifications, responsibilities, employment_type,
        primary_skills, secondary_skills, tertiary_skills, jd_file_path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        jd.job_title,
        jd.company_name,
        jd.location,
        jd.experience_required,
        json.dumps(jd.qualifications),
        json.dumps(jd.responsibilities),
        jd.employment_type,
        json.dumps(jd.primary_skills),
        json.dumps(jd.secondary_skills),
        json.dumps(jd.tertiary_skills),
        jd.jd_file_path
    )
    try:
        execute_non_query(query, params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert error: {str(e)}")

@router.post("/upload-jd", response_model=JobDescription, status_code=201)
def upload_job_description(file: UploadFile = File(...)):
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF and DOCX allowed.")

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
        jd_text = extract_pdf_text(file_path)
    else:
        jd_text = extract_docx_text(file_path)
    if not jd_text:
        raise HTTPException(status_code=400, detail="No text extracted from file.")

    # Call Gemini API
    ai_data = call_gemini_api(jd_text)
    if not ai_data.get("job_title"):
        raise HTTPException(status_code=422, detail="AI did not return required job details.")

    # Build JD object
    jd = JobDescription(**ai_data, jd_file_path=file_path)

    # Insert into DB
    insert_job_description(jd)

    return jd


@router.get("/jd", response_model=List[JobDescription])
def get_all_jd():
    """Get all job description details from the database."""
    query = "SELECT job_title,company_name,location,experience_required,qualifications,responsibilities,employment_type,primary_skills,secondary_skills,tertiary_skills,jd_file_path from job_descriptions"
    try:
        from database import execute_query
        rows = execute_query(query)
        jds = []
        for row in rows:
            jds.append(JobDescription(
                job_title=row[0],
                company_name=row[1],
                location=row[2],
                experience_required=str(row[3]) if row[3] is not None else "",
                qualifications=json.loads(row[4]) if row[4] else [],
                responsibilities=json.loads(row[5]) if row[5] else [],
                employment_type=row[6] if row[6] else "",
                primary_skills=json.loads(row[7]) if row[7] else [],
                secondary_skills=json.loads(row[8]) if row[8] else [],
                tertiary_skills=json.loads(row[9]) if row[9] else [],
                jd_file_path=row[10],
            ))
        return jds
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    




@router.post("/resume_matcher/")
async def create_upload_file(resume: UploadFile,jd: UploadFile):
        # ... file processing logic ...
    with pdfplumber.open(resume.file) as pdf:
        pages = pdf.pages
        resume_text = ""

        for page in pages:
            resume_text += page.extract_text()
            
    with pdfplumber.open(jd.file) as pdf:
        pages = pdf.pages
        jd_text = ""

        for page in pages:
            jd_text += page.extract_text()

    try:
        # Initialize the Gemini client with the API key from environment variables
        # Ensure GEMINI_API_KEY is set in your environment
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set in environment variables.")

        client = genai.Client(api_key=api_key)

        context = """
        I have given resume and job description, your work is to match the resume with jd,
        
        consider following points while matching and match one by one and see all skills dont forget anything 
        1. list the candidate detials in seperate line like name,email,phone number etc
        2. get the candidate highest education detials
        3.get the internship /experiance in compony
        4. similarly list skills in candidate
        5. match the skills using job description and list them display matching and unmatched skills 
        6. find the skill matching percentage 
        7. If matching percentage is more thann 70 display Resume qulified succesfully otherwise display resume not qualified
        8. give summery for selecting or not selecting the resume in 3 sentesnce
        Give all above information in seperate line
        and read jd and resume properly
        provide the output in structaral way with json format
        """
        context_2 ="""
        You are an AI assistant specialized in resume and job description analysis.
        Your task is to compare a job description with a resume and provide a detailed assessment.
        """
        
        prompt=f"""
        ---
        Job Description:
        {jd_text}
        ---

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
                #esponse_json_schema=Qa.model_json_schema()
            ),
            contents=[prompt],
        )
        return  parse_response(response)
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
                    detail=f"Model response could not be parsed as JSON. Raw text: '{response.text}'. Error: {json_e}"
                )
     else:
        # If response.parsed is not None, return it directly
        return response.parsed
