"""Pure deterministic composition of individual recommendation score components."""

from app.scoring.domain import CandidateProfile, JobPosting
from app.scoring.config import DEFAULT_WEIGHTS, ScoringWeights
from app.scoring.experience import score_experience
from app.scoring.location import score_location
from app.scoring.salary import score_salary
from app.scoring.skills import score_skills
from app.schemas.recommendation import (
    ComponentBreakdown,
    LocationBreakdown,
    MatchCount,
    RecommendationResponse,
    ScoreBreakdown,
    SkillsBreakdown,
)


def score_candidate_for_job(
    candidate: CandidateProfile, job: JobPosting, weights: ScoringWeights = DEFAULT_WEIGHTS
) -> RecommendationResponse | None:
    """Score an eligible job or return None if a must-have requirement is missing."""
    skill_result = score_skills(candidate.skills, job.required_skills, weights.skills)
    if skill_result is None:
        return None
    experience = score_experience(candidate.years_of_experience, job.min_years_experience, weights.experience)
    location = score_location(candidate.location, job.location, job.remote_allowed, weights.location)
    salary = score_salary(candidate.expected_salary, job.salary_min, job.salary_max, weights.salary)
    total = round(max(0.0, min(100.0, skill_result.score + experience + location.score + salary)), 2)
    return RecommendationResponse(
        job_id=job.id,
        title=job.title,
        score=total,
        breakdown=ScoreBreakdown(
            skills=SkillsBreakdown(
                score=skill_result.score,
                maximum=weights.skills,
                must_have=MatchCount(matched=skill_result.matched_must_have, total=skill_result.total_must_have),
                nice_to_have=MatchCount(matched=skill_result.matched_nice_to_have, total=skill_result.total_nice_to_have),
            ),
            experience=ComponentBreakdown(score=experience, maximum=weights.experience),
            location=LocationBreakdown(score=location.score, maximum=weights.location, reason=location.reason),
            salary=ComponentBreakdown(score=salary, maximum=weights.salary),
        ),
    )
