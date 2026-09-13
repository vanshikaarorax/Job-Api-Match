from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_scoring_weights
from app.models.candidate import Candidate
from app.models.job import Job
from app.schemas.recommendation import CandidateRecommendationResponse, RecommendationResponse
from app.scoring.domain import CandidateProfile, JobPosting, SkillRequirement
from app.scoring.scorer import score_candidate_for_job


def _candidate_profile(candidate: Candidate) -> CandidateProfile:
    return CandidateProfile(
        id=candidate.id,
        skills=tuple(skill.skill_name for skill in candidate.skills),
        years_of_experience=candidate.years_of_experience,
        location=candidate.location,
        expected_salary=candidate.expected_salary,
    )


def _job_posting(job: Job) -> JobPosting:
    return JobPosting(
        id=job.id,
        title=job.title,
        required_skills=tuple(
            SkillRequirement(name=skill.skill_name, skill_type=skill.skill_type.value)
            for skill in job.required_skills
        ),
        min_years_experience=job.min_years_experience,
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        remote_allowed=job.remote_allowed,
    )


def get_recommendations(db: Session, candidate: Candidate, limit: int) -> list[RecommendationResponse]:
    """Load jobs, score them through the pure scorer, then rank before limiting."""
    profile = _candidate_profile(candidate)
    weights = get_scoring_weights()
    jobs = db.scalars(select(Job)).all()
    recommendations = [
        result
        for job in jobs
        if ((result := score_candidate_for_job(profile, _job_posting(job), weights)) is not None)
    ]
    return sorted(recommendations, key=lambda recommendation: recommendation.score, reverse=True)[:limit]


def get_candidate_recommendations(
    db: Session, job: Job, limit: int
) -> list[CandidateRecommendationResponse]:
    """Score every candidate against one job, using the same forward scorer."""
    posting = _job_posting(job)
    weights = get_scoring_weights()
    results = []
    for candidate in db.scalars(select(Candidate)).all():
        score = score_candidate_for_job(_candidate_profile(candidate), posting, weights)
        if score is not None:
            results.append(
                CandidateRecommendationResponse(
                    candidate_id=candidate.id,
                    name=candidate.name,
                    score=score.score,
                    breakdown=score.breakdown,
                )
            )
    return sorted(results, key=lambda recommendation: recommendation.score, reverse=True)[:limit]
