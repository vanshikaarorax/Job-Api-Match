from pydantic import Field

from app.schemas.common import APIModel


class MatchCount(APIModel):
    matched: int = Field(ge=0)
    total: int = Field(ge=0)


class SkillsBreakdown(APIModel):
    score: float = Field(ge=0)
    maximum: float = Field(50, serialization_alias="max")
    must_have: MatchCount = Field(serialization_alias="mustHave")
    nice_to_have: MatchCount = Field(serialization_alias="niceToHave")


class ComponentBreakdown(APIModel):
    score: float = Field(ge=0)
    maximum: float = Field(serialization_alias="max")


class LocationBreakdown(ComponentBreakdown):
    reason: str


class ScoreBreakdown(APIModel):
    skills: SkillsBreakdown
    experience: ComponentBreakdown
    location: LocationBreakdown
    salary: ComponentBreakdown


class RecommendationResponse(APIModel):
    job_id: int = Field(serialization_alias="jobId")
    title: str
    score: float = Field(ge=0, le=100)
    breakdown: ScoreBreakdown


class RecommendationsResponse(APIModel):
    candidate_id: int = Field(serialization_alias="candidateId")
    results: list[RecommendationResponse]


class CandidateRecommendationResponse(APIModel):
    candidate_id: int = Field(serialization_alias="candidateId")
    name: str
    score: float = Field(ge=0, le=100)
    breakdown: ScoreBreakdown


class JobRecommendationsResponse(APIModel):
    job_id: int = Field(serialization_alias="jobId")
    results: list[CandidateRecommendationResponse]
