from pydantic import BaseModel
from typing import List, Optional

class JobDescription(BaseModel):
    text: str
    source: str  # "file", "text", "generated"

class Candidate(BaseModel):
    filename: str
    resume_text: str

class MatchingResult(BaseModel):
    candidate: Candidate
    score: float
    missing_skills: List[str]
    remarks: str
    interview_email: Optional[str] = None
    rejection_email: Optional[str] = None
