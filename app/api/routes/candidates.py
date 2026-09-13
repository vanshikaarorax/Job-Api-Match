from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.candidate import CandidateCreate, CandidateResponse
from app.services.candidate_service import create_candidate, get_candidate, serialize_candidate

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED, response_model_by_alias=True)
def create_candidate_route(payload: CandidateCreate, db: Session = Depends(get_db)) -> CandidateResponse:
    return serialize_candidate(create_candidate(db, payload))


@router.get("/{candidate_id}", response_model=CandidateResponse, response_model_by_alias=True)
def get_candidate_route(candidate_id: int, db: Session = Depends(get_db)) -> CandidateResponse:
    candidate = get_candidate(db, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return serialize_candidate(candidate)
