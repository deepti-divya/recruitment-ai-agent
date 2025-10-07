from typing import List
from app.models.schemas import Candidate, MatchingResult
from app.services.ai_service import AIService

class MatchingService:
    def _init_(self):
        self.ai_service = AIService()

    async def evaluate_candidates(self, jd_text: str, candidates: List[Candidate]) -> List[MatchingResult]:
        """Evaluate all candidates against job description"""
        results = []
        
        for candidate in candidates:
            # Calculate similarity score
            score = await self.ai_service.calculate_similarity(jd_text, candidate.resume_text)
            
            # Analyze missing skills
            missing_skills, remarks = await self.ai_service.analyze_missing_skills(jd_text, candidate.resume_text)
            
            # Create result
            result = MatchingResult(
                candidate=candidate,
                score=score,
                missing_skills=missing_skills,
                remarks=remarks
            )
            
            results.append(result)
        
        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results
