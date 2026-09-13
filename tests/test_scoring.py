import pytest

from app.scoring.config import ScoringWeights
from app.scoring.domain import CandidateProfile, JobPosting, SkillRequirement
from app.scoring.experience import score_experience
from app.scoring.location import score_location
from app.scoring.salary import score_salary
from app.scoring.scorer import score_candidate_for_job
from app.scoring.skills import score_skills


def candidate(*skills: str, years: float = 3, location: str = "Delhi", expected: float = 100) -> CandidateProfile:
    return CandidateProfile(1, skills, years, location, expected)


def job(
    requirements: tuple[SkillRequirement, ...] = (), *, years: float = 3, location: str = "Delhi",
    salary_min: float = 100, salary_max: float = 200, remote: bool = False, job_id: int = 1,
) -> JobPosting:
    return JobPosting(job_id, f"Job {job_id}", requirements, years, location, salary_min, salary_max, remote)


def requirement(name: str, kind: str) -> SkillRequirement:
    return SkillRequirement(name, kind)


def test_missing_one_must_have_excludes_job():
    result = score_candidate_for_job(candidate("Python"), job((requirement("Python", "must_have"), requirement("FastAPI", "must_have"))))
    assert result is None


def test_missing_multiple_must_haves_excludes_job():
    result = score_candidate_for_job(candidate("Python"), job((requirement("FastAPI", "must_have"), requirement("SQL", "must_have"))))
    assert result is None


def test_all_must_haves_are_eligible_and_normalized():
    result = score_candidate_for_job(candidate(" python ", "FASTapi"), job((requirement("PYTHON", "must_have"), requirement("FastAPI", "must_have"))))
    assert result is not None
    assert result.breakdown.skills.must_have.model_dump() == {"matched": 2, "total": 2}


def test_nice_to_have_match_increases_skill_score():
    requirements = (requirement("Python", "must_have"), requirement("Docker", "nice_to_have"))
    without_nice = score_skills(["Python"], requirements)
    with_nice = score_skills(["Python", "Docker"], requirements)
    assert without_nice is not None and without_nice.score == 40
    assert with_nice is not None and with_nice.score == 50


def test_zero_nice_to_haves_gets_full_ten_points():
    result = score_skills(["Python"], [requirement("Python", "must_have")])
    assert result is not None
    assert result.score == 50
    assert result.total_nice_to_have == 0


@pytest.mark.parametrize(("candidate_years", "required_years", "expected"), [(5, 5, 20), (6, 5, 20), (3, 5, 12), (0, 5, 0), (0, 0, 20)])
def test_experience_scores(candidate_years, required_years, expected):
    assert score_experience(candidate_years, required_years) == expected


def test_exact_location_scores_full_points_with_normalization():
    assert score_location(" Delhi ", "delhi", False).score == 15


def test_remote_location_mismatch_scores_ten_points():
    result = score_location("Delhi", "Bangalore", True)
    assert (result.score, result.reason) == (10, "remote")


def test_non_remote_location_mismatch_scores_zero():
    assert score_location("Delhi", "Bangalore", False).score == 0


@pytest.mark.parametrize(("expected", "minimum", "maximum", "score"), [
    (100, 50, 90, 0), (100, 50, 200, 10), (100, 100, 200, 15),
    (100, 100, 100, 15), (101, 100, 100, 0),
])
def test_salary_piecewise_scores(expected, minimum, maximum, score):
    assert score_salary(expected, minimum, maximum) == score


def test_final_score_is_clamped_to_100():
    result = score_candidate_for_job(candidate("Python", years=999, expected=0), job((requirement("Python", "must_have"),), years=0, salary_min=1, salary_max=1))
    assert result is not None and result.score == 100


def test_final_score_is_never_below_zero():
    result = score_candidate_for_job(candidate("Python", years=0, location="A", expected=1000), job((requirement("Python", "must_have"),), years=5, location="B", salary_min=1, salary_max=2))
    assert result is not None and result.score == 50


def test_breakdown_has_exact_scores_and_counts():
    result = score_candidate_for_job(
        candidate("Python", "Docker", years=3, location="Delhi", expected=100),
        job((requirement("Python", "must_have"), requirement("Docker", "nice_to_have"), requirement("Kubernetes", "nice_to_have")), years=5, location="Mumbai", salary_min=50, salary_max=200, remote=True),
    )
    assert result is not None
    assert result.score == 77.0
    assert result.breakdown.skills.model_dump() == {
        "score": 45.0, "maximum": 50.0,
        "must_have": {"matched": 1, "total": 1}, "nice_to_have": {"matched": 1, "total": 2},
    }
    assert result.breakdown.experience.score == 12
    assert result.breakdown.location.score == 10
    assert result.breakdown.salary.score == 10


def test_configurable_weights_are_applied_to_the_same_scorer():
    weights = ScoringWeights(skills=40, experience=30, location=15, salary=15)
    result = score_candidate_for_job(
        candidate("Python", years=3, expected=100),
        job((requirement("Python", "must_have"),), years=3, salary_min=100, salary_max=200),
        weights,
    )
    assert result is not None
    assert result.score == 100
    assert result.breakdown.skills.score == 40
    assert result.breakdown.experience.maximum == 30


def test_invalid_weights_are_rejected():
    with pytest.raises(ValueError, match="sum to 100"):
        ScoringWeights(skills=60, experience=20, location=15, salary=15)
