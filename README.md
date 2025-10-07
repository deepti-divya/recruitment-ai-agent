# Recruitment AI Agent

A sophisticated AI-powered recruitment platform that automates candidate evaluation.

## Features
- Job Description Management (Upload, Manual, AI Generation)
- Resume Analysis (PDF, DOC, DOCX support)  
- AI-Powered Matching with scoring
- Automated email generation

## Technology Stack
- FastAPI Backend
- Sentence Transformers for AI matching
- Bootstrap Frontend
- Python 3.8+

## Installation Steps
1. Extract project files to desired location
2. Open command prompt in the project directory
3. Create virtual environment: python -m venv venv
4. Activate environment: venv\Scripts\activate
5. Install dependencies: pip install -r requirements.txt
6. Start application: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
7. Open browser and navigate to http://localhost:8000

## Usage Guide
- Upload Job Description using any of three methods
- Upload multiple resumes (up to 10 files)
- View AI-generated matching scores and analysis
- Copy personalized emails for candidates

The project is production-ready and demonstrates modern AI integration in recruitment workflows.