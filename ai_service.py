import os
import openai
from typing import List
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from app.models.schemas import MatchingResult

class AIService:
    def _init_(self):
        # Initialize sentence transformer model for embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize OpenAI if API key is available
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

    async def generate_job_description(self, job_title: str, years_experience: str, 
                                     must_have_skills: str, company_name: str, 
                                     employment_type: str, industry: str, location: str) -> str:
        """Generate job description using AI"""
        
        prompt = f"""
        Create a professional job description for the following position:
        
        Job Title: {job_title}
        Years of Experience: {years_experience}
        Must-have Skills: {must_have_skills}
        Company: {company_name}
        Employment Type: {employment_type}
        Industry: {industry}
        Location: {location}
        
        Please include:
        1. Job summary
        2. Key responsibilities
        3. Required qualifications and skills
        4. Preferred qualifications
        5. What we offer
        
        Make it professional and engaging.
        """
        
        if self.openai_api_key:
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception:
                # Fallback to template-based generation if OpenAI fails
                return self._generate_jd_template(job_title, years_experience, must_have_skills, 
                                                company_name, employment_type, industry, location)
        else:
            return self._generate_jd_template(job_title, years_experience, must_have_skills, 
                                            company_name, employment_type, industry, location)

    def _generate_jd_template(self, job_title: str, years_experience: str, 
                            must_have_skills: str, company_name: str, 
                            employment_type: str, industry: str, location: str) -> str:
        """Fallback template-based JD generation"""
        skills_list = [skill.strip() for skill in must_have_skills.split(',')]
        
        return f"""
        Job Title: {job_title}
        Company: {company_name}
        Location: {location}
        Employment Type: {employment_type}
        Industry: {industry}
        
        Job Summary:
        We are seeking an experienced {job_title} with {years_experience} years of experience to join our dynamic team at {company_name}. The ideal candidate will play a key role in driving success in the {industry} industry.
        
        Key Responsibilities:
        • Develop and implement strategic initiatives
        • Collaborate with cross-functional teams
        • Drive projects from conception to completion
        • Analyze and optimize business processes
        
        Required Qualifications:
        • {years_experience} years of relevant experience
        • Proficiency in: {', '.join(skills_list)}
        • Strong communication and leadership skills
        • Bachelor's degree in relevant field
        
        Preferred Qualifications:
        • Master's degree or higher
        • Experience in {industry} industry
        • Professional certifications
        
        What We Offer:
        • Competitive salary and benefits
        • Professional development opportunities
        • Dynamic and inclusive work environment
        • Career growth potential
        """

    async def calculate_similarity(self, jd_text: str, resume_text: str) -> float:
        """Calculate similarity score between JD and resume using sentence transformers"""
        try:
            # Encode both texts
            jd_embedding = self.model.encode(jd_text, convert_to_tensor=True)
            resume_embedding = self.model.encode(resume_text, convert_to_tensor=True)
            
            # Calculate cosine similarity
            cosine_score = util.pytorch_cos_sim(jd_embedding, resume_embedding).item()
            
            # Convert to percentage (0-100)
            score = round(cosine_score * 100, 2)
            return max(0, min(100, score))  # Ensure score is between 0-100
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    async def analyze_missing_skills(self, jd_text: str, resume_text: str) -> tuple:
        """Analyze missing skills and generate remarks"""
        # Extract common technical skills keywords
        technical_skills = [
            'python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes',
            'machine learning', 'ai', 'data analysis', 'project management',
            'agile', 'scrum', 'react', 'angular', 'vue', 'node.js', 'express',
            'mongodb', 'postgresql', 'mysql', 'git', 'jenkins', 'ci/cd',
            'rest api', 'graphql', 'microservices', 'devops'
        ]
        
        jd_lower = jd_text.lower()
        resume_lower = resume_text.lower()
        
        missing_skills = []
        present_skills = []
        
        for skill in technical_skills:
            if skill in jd_lower:
                if skill not in resume_lower:
                    missing_skills.append(skill.title())
                else:
                    present_skills.append(skill.title())
        
        # Generate remarks
        remarks = self._generate_remarks(present_skills, missing_skills, len(present_skills))
        
        return missing_skills, remarks

    def _generate_remarks(self, present_skills: List[str], missing_skills: List[str], skill_count: int) -> str:
        """Generate intelligent remarks based on skills analysis"""
        if skill_count == 0:
            return "Candidate lacks most required technical skills"
        elif len(missing_skills) == 0:
            return "Excellent match! Candidate possesses all key technical skills"
        elif len(missing_skills) <= 2:
            return f"Strong candidate with most required skills. Missing: {', '.join(missing_skills[:2])}"
        elif len(missing_skills) <= 4:
            return f"Moderate match. Has core skills but missing: {', '.join(missing_skills[:3])}"
        else:
            return f"Limited match. Candidate lacks several key skills including {', '.join(missing_skills[:3])}"

    async def generate_interview_email(self, result: MatchingResult) -> str:
        """Generate personalized interview email"""
        candidate_name = result.candidate.filename.split('.')[0]
        
        email_template = f"""
        Subject: Interview Invitation - Congratulations!

        Dear {candidate_name},

        Thank you for applying to our position. We were impressed with your background and experience, particularly your strengths in key areas that match our requirements.

        Your application scored {result.score}% relevance to our position, which is quite notable!

        We would like to invite you for an interview to discuss your qualifications and how you can contribute to our team.

        Please let us know your availability for a virtual meeting next week.

        Best regards,
        Recruitment Team
        """
        
        return email_template

    async def generate_rejection_email(self, result: MatchingResult) -> str:
        """Generate personalized rejection email"""
        candidate_name = result.candidate.filename.split('.')[0]
        
        email_template = f"""
        Subject: Update on Your Application

        Dear {candidate_name},

        Thank you for taking the time to apply for our position and for sharing your qualifications with us.

        While we were impressed with your background, we have decided to move forward with candidates whose experience more closely aligns with our current requirements.

        We appreciate your interest in our company and encourage you to apply for future positions that may be a better fit.

        We wish you the best in your job search.

        Best regards,
        Recruitment Team
        """
        
        return email_template
