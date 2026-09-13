from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendation import JobRecommendationsResponse
from app.services.job_service import get_job
from app.services.recommendation_service import get_candidate_recommendations

router = APIRouter(prefix="/jobs", tags=["recommendations"])


@router.get("/{job_id}/recommendations", response_model=JobRecommendationsResponse, response_model_by_alias=True)
def candidate_recommendations_route(
    job_id: int,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    db: Session = Depends(get_db),
) -> JobRecommendationsResponse:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobRecommendationsResponse(job_id=job.id, results=get_candidate_recommendations(db, job, limit))
