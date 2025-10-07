import os
import re
from typing import List

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
    
    return text.strip()

def extract_skills_from_text(text: str) -> List[str]:
    """Extract potential skills from text"""
    # Common technical skills patterns
    skill_patterns = [
        r'python', r'java', r'javascript', r'typescript', r'c\+\+', r'c#',
        r'sql', r'mongodb', r'postgresql', r'mysql', r'redis',
        r'aws', r'azure', r'gcp', r'docker', r'kubernetes',
        r'react', r'angular', r'vue', r'node\.js', r'express',
        r'machine learning', r'ai', r'data analysis', r'data science',
        r'agile', r'scrum', r'devops', r'ci/cd', r'git',
        r'rest api', r'graphql', r'microservices', r'api development'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for pattern in skill_patterns:
        if re.search(pattern, text_lower):
            skill_name = pattern.replace('\\', '').replace('/', '')
            found_skills.append(skill_name.title())
    
    return list(set(found_skills))

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()
