from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate import Candidate, CandidateSkill
from app.schemas.candidate import CandidateCreate, CandidateResponse


def create_candidate(db: Session, payload: CandidateCreate) -> Candidate:
    candidate = Candidate(
        name=payload.name,
        years_of_experience=payload.years_of_experience,
        location=payload.location,
        expected_salary=payload.expected_salary,
        skills=[CandidateSkill(skill_name=skill) for skill in payload.skills],
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def get_candidate(db: Session, candidate_id: int) -> Candidate | None:
    return db.scalar(select(Candidate).where(Candidate.id == candidate_id))


def serialize_candidate(candidate: Candidate) -> CandidateResponse:
    return CandidateResponse(
        id=candidate.id, name=candidate.name, skills=[skill.skill_name for skill in candidate.skills],
        years_of_experience=candidate.years_of_experience, location=candidate.location,
        expected_salary=candidate.expected_salary, created_at=candidate.created_at,
    )
