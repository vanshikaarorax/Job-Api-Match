from datetime import datetime

from pydantic import Field, field_validator

from app.schemas.common import APIModel
from app.scoring.skills import normalize_text


def normalize_skill(value: str) -> str:
    normalized = normalize_text(value)
    if not normalized:
        raise ValueError("skill cannot be blank")
    return normalized


class CandidateCreate(APIModel):
    name: str = Field(min_length=1, max_length=255)
    skills: list[str] = Field(min_length=1)
    years_of_experience: float = Field(ge=0, alias="yearsOfExperience")
    location: str = Field(min_length=1, max_length=255)
    expected_salary: float = Field(ge=0, alias="expectedSalary")

    @field_validator("name", "location")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("value cannot be blank")
        return value

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, values: list[str]) -> list[str]:
        normalized = [normalize_skill(value) for value in values]
        if len(set(normalized)) != len(normalized):
            raise ValueError("skills must be unique after normalization")
        return normalized


class CandidateResponse(APIModel):
    id: int
    name: str
    skills: list[str]
    years_of_experience: float = Field(serialization_alias="yearsOfExperience")
    location: str
    expected_salary: float = Field(serialization_alias="expectedSalary")
    created_at: datetime = Field(serialization_alias="createdAt")
