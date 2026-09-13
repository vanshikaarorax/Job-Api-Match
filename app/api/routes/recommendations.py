from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendation import RecommendationsResponse
from app.services.candidate_service import get_candidate
from app.services.recommendation_service import get_recommendations

router = APIRouter(prefix="/candidates", tags=["recommendations"])


@router.get("/{candidate_id}/recommendations", response_model=RecommendationsResponse, response_model_by_alias=True)
def recommendations_route(
    candidate_id: int,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    candidate = get_candidate(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return RecommendationsResponse(candidate_id=candidate.id, results=get_recommendations(db, candidate, limit))
