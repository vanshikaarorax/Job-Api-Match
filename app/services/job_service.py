from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job, JobSkill
from app.schemas.job import JobCreate, JobResponse, RequiredSkillResponse, SalaryRangeResponse


def create_job(db: Session, payload: JobCreate) -> Job:
    job = Job(
        title=payload.title, min_years_experience=payload.min_years_experience,
        location=payload.location, salary_min=payload.salary_range.minimum,
        salary_max=payload.salary_range.maximum, remote_allowed=payload.remote_allowed,
        required_skills=[JobSkill(skill_name=skill.name, skill_type=skill.type) for skill in payload.required_skills],
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: int) -> Job | None:
    return db.scalar(select(Job).where(Job.id == job_id))


def serialize_job(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id, title=job.title,
        required_skills=[RequiredSkillResponse(name=skill.skill_name, type=skill.skill_type) for skill in job.required_skills],
        min_years_experience=job.min_years_experience, location=job.location,
        salary_range=SalaryRangeResponse(minimum=job.salary_min, maximum=job.salary_max),
        remote_allowed=job.remote_allowed, created_at=job.created_at,
    )
