"""Validated, injectable scoring weights."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringWeights:
    skills: float = 50.0
    experience: float = 20.0
    location: float = 15.0
    salary: float = 15.0

    def __post_init__(self) -> None:
        values = (self.skills, self.experience, self.location, self.salary)
        if any(value < 0 for value in values):
            raise ValueError("scoring weights must be non-negative")
        if round(sum(values), 8) != 100:
            raise ValueError("scoring weights must sum to 100")


DEFAULT_WEIGHTS = ScoringWeights()
