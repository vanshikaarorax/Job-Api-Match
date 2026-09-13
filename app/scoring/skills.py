"""Skill normalization, eligibility, and score calculation."""

from dataclasses import dataclass
from typing import Iterable

from app.scoring.domain import SkillRequirement

DEFAULT_SKILLS_MAX = 50.0


def normalize_text(value: str) -> str:
    """Casefold and collapse whitespace for deterministic text comparisons."""
    return " ".join(value.split()).casefold()


@dataclass(frozen=True)
class SkillScore:
    matched_must_have: int
    total_must_have: int
    matched_nice_to_have: int
    total_nice_to_have: int
    score: float


def score_skills(
    candidate_skills: Iterable[str], requirements: Iterable[SkillRequirement], maximum: float = DEFAULT_SKILLS_MAX
) -> SkillScore | None:
    """Return None for missing must-haves, otherwise calculate the 50-point score."""
    candidate_set = {normalize_text(skill) for skill in candidate_skills}
    requirements_list = list(requirements)
    must_haves = [skill for skill in requirements_list if skill.skill_type == "must_have"]
    nice_to_haves = [skill for skill in requirements_list if skill.skill_type == "nice_to_have"]
    matched_must = sum(normalize_text(skill.name) in candidate_set for skill in must_haves)
    if matched_must != len(must_haves):
        return None

    matched_nice = sum(normalize_text(skill.name) in candidate_set for skill in nice_to_haves)
    must_have_max = maximum * 0.8
    nice_to_have_max = maximum * 0.2
    nice_score = nice_to_have_max if not nice_to_haves else nice_to_have_max * matched_nice / len(nice_to_haves)
    return SkillScore(
        matched_must_have=matched_must,
        total_must_have=len(must_haves),
        matched_nice_to_have=matched_nice,
        total_nice_to_have=len(nice_to_haves),
        score=round(must_have_max + nice_score, 2),
    )
