"""Salary-fit scoring rules."""

DEFAULT_SALARY_MAX = 15.0


def score_salary(
    expected_salary: float, salary_min: float, salary_max: float, maximum: float = DEFAULT_SALARY_MAX
) -> float:
    """Score the proportion of the advertised range meeting salary expectation."""
    if salary_min == salary_max:
        return maximum if salary_min >= expected_salary else 0.0
    if salary_max < expected_salary:
        return 0.0
    if salary_min >= expected_salary:
        return maximum
    score = maximum * (salary_max - expected_salary) / (salary_max - salary_min)
    return round(max(0.0, min(maximum, score)), 2)
