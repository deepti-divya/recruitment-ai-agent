from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import os
import shutil
from pathlib import Path

from app.models.schemas import JobDescription, Candidate, MatchingResult
from app.services.file_processor import FileProcessor
from app.services.ai_service import AIService
from app.services.matching_service import MatchingService

app = FastAPI(title="Recruitment AI Agent", version="1.0.0")

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize services
file_processor = FileProcessor()
ai_service = AIService()
matching_service = MatchingService()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate_jd")
async def generate_job_description(
    job_title: str = Form(...),
    years_experience: str = Form(...),
    must_have_skills: str = Form(...),
    company_name: str = Form(...),
    employment_type: str = Form(...),
    industry: str = Form(...),
    location: str = Form(...)
):
    """Generate job description using AI"""
    try:
        jd_text = await ai_service.generate_job_description(
            job_title=job_title,
            years_experience=years_experience,
            must_have_skills=must_have_skills,
            company_name=company_name,
            employment_type=employment_type,
            industry=industry,
            location=location
        )
        return {"job_description": jd_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating JD: {str(e)}")

@app.post("/upload_jd")
async def upload_job_description(
    jd_file: Optional[UploadFile] = File(None),
    jd_text: Optional[str] = Form(None)
):
    """Upload job description via file or text"""
    try:
        if jd_file:
            # Save uploaded file
            file_path = UPLOAD_DIR / f"jd_{jd_file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(jd_file.file, buffer)
            
            # Extract text from file
            jd_content = await file_processor.extract_text_from_file(str(file_path))
        elif jd_text:
            jd_content = jd_text
        else:
            raise HTTPException(status_code=400, detail="Either file or text must be provided")
        
        return {"job_description": jd_content, "message": "JD processed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing JD: {str(e)}")

@app.post("/evaluate_candidates", response_class=HTMLResponse)
async def evaluate_candidates(
    request: Request,
    job_description: str = Form(...),
    resume_files: List[UploadFile] = File(...)
):
    """Evaluate candidates against job description"""
    try:
        if len(resume_files) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 resumes allowed")
        
        candidates = []
        for resume_file in resume_files:
            # Save resume file
            file_path = UPLOAD_DIR / f"resume_{resume_file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(resume_file.file, buffer)
            
            # Extract text from resume
            resume_text = await file_processor.extract_text_from_file(str(file_path))
            
            # Create candidate object
            candidate = Candidate(
                filename=resume_file.filename,
                resume_text=resume_text
            )
            candidates.append(candidate)
        
        # Evaluate candidates
        results = await matching_service.evaluate_candidates(job_description, candidates)
        
        # Generate emails
        for result in results:
            result.interview_email = await ai_service.generate_interview_email(result)
            result.rejection_email = await ai_service.generate_rejection_email(result)
        
        return templates.TemplateResponse(
            "results.html", 
            {
                "request": request, 
                "job_description": job_description[:500] + "..." if len(job_description) > 500 else job_description,
                "results": results,
                "best_candidate": max(results, key=lambda x: x.score) if results else None
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating candidates: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Recruitment AI Agent"}

if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
