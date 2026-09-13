"""Location-fit scoring rules."""

from dataclasses import dataclass

from app.scoring.skills import normalize_text

DEFAULT_LOCATION_MAX = 15.0


@dataclass(frozen=True)
class LocationScore:
    score: float
    reason: str


def score_location(
    candidate_location: str, job_location: str, remote_allowed: bool, maximum: float = DEFAULT_LOCATION_MAX
) -> LocationScore:
    if normalize_text(candidate_location) == normalize_text(job_location):
        return LocationScore(score=maximum, reason="exact_match")
    if remote_allowed:
        return LocationScore(score=round(maximum * 2 / 3, 2), reason="remote")
    return LocationScore(score=0.0, reason="mismatch")
