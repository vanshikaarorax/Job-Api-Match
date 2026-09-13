"""Plain domain objects consumed by the recommendation scorer."""

from dataclasses import dataclass

@dataclass(frozen=True)
class CandidateProfile:
    id: int
    skills: tuple[str, ...]
    years_of_experience: float
    location: str
    expected_salary: float


@dataclass(frozen=True)
class SkillRequirement:
    name: str
    skill_type: str


@dataclass(frozen=True)
class JobPosting:
    id: int
    title: str
    required_skills: tuple[SkillRequirement, ...]
    min_years_experience: float
    location: str
    salary_min: float
    salary_max: float
    remote_allowed: bool
