from datetime import datetime

from pydantic import Field, model_validator

from app.models.job import SkillType
from app.schemas.candidate import normalize_skill
from app.schemas.common import APIModel


class RequiredSkillCreate(APIModel):
    name: str = Field(min_length=1, max_length=255)
    type: SkillType

    @model_validator(mode="after")
    def normalize_name(self) -> "RequiredSkillCreate":
        self.name = normalize_skill(self.name)
        return self


class SalaryRange(APIModel):
    minimum: float = Field(ge=0, alias="min")
    maximum: float = Field(ge=0, alias="max")

    @model_validator(mode="after")
    def validate_range(self) -> "SalaryRange":
        if self.maximum < self.minimum:
            raise ValueError("salary max cannot be lower than salary min")
        return self


class JobCreate(APIModel):
    title: str = Field(min_length=1, max_length=255)
    required_skills: list[RequiredSkillCreate] = Field(min_length=1, alias="requiredSkills")
    min_years_experience: float = Field(ge=0, alias="minYearsExperience")
    location: str = Field(min_length=1, max_length=255)
    salary_range: SalaryRange = Field(alias="salaryRange")
    remote_allowed: bool = Field(alias="remoteAllowed")

    @model_validator(mode="after")
    def validate_text_and_unique_skills(self) -> "JobCreate":
        self.title = " ".join(self.title.split())
        self.location = " ".join(self.location.split())
        if not self.title or not self.location:
            raise ValueError("title and location cannot be blank")
        skill_keys = [(skill.name, skill.type) for skill in self.required_skills]
        if len(set(skill_keys)) != len(skill_keys):
            raise ValueError("required skills must be unique by name and type")
        return self


class RequiredSkillResponse(APIModel):
    name: str
    type: SkillType


class SalaryRangeResponse(APIModel):
    minimum: float = Field(serialization_alias="min")
    maximum: float = Field(serialization_alias="max")


class JobResponse(APIModel):
    id: int
    title: str
    required_skills: list[RequiredSkillResponse] = Field(serialization_alias="requiredSkills")
    min_years_experience: float = Field(serialization_alias="minYearsExperience")
    location: str
    salary_range: SalaryRangeResponse = Field(serialization_alias="salaryRange")
    remote_allowed: bool = Field(serialization_alias="remoteAllowed")
    created_at: datetime = Field(serialization_alias="createdAt")
