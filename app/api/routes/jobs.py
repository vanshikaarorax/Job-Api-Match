from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import create_job, get_job, serialize_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED, response_model_by_alias=True)
def create_job_route(payload: JobCreate, db: Session = Depends(get_db)) -> JobResponse:
    return serialize_job(create_job(db, payload))


@router.get("/{job_id}", response_model=JobResponse, response_model_by_alias=True)
def get_job_route(job_id: int, db: Session = Depends(get_db)) -> JobResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return serialize_job(job)
