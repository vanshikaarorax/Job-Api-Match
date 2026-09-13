"""Experience-fit scoring rules."""

DEFAULT_EXPERIENCE_MAX = 20.0


def score_experience(
    candidate_years: float, minimum_years: float, maximum: float = DEFAULT_EXPERIENCE_MAX
) -> float:
    """Score experience proportionally below the requirement without excluding it."""
    if minimum_years == 0 or candidate_years >= minimum_years:
        return maximum
    return round(max(0.0, min(maximum, maximum * candidate_years / minimum_years)), 2)
