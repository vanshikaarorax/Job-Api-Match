from app.config import get_scoring_weights, get_settings


def test_environment_weight_overrides_are_loaded(monkeypatch):
    monkeypatch.setenv("SCORING_SKILLS_WEIGHT", "40")
    monkeypatch.setenv("SCORING_EXPERIENCE_WEIGHT", "30")
    monkeypatch.setenv("SCORING_LOCATION_WEIGHT", "15")
    monkeypatch.setenv("SCORING_SALARY_WEIGHT", "15")
    get_settings.cache_clear()
    try:
        weights = get_scoring_weights()
        assert (weights.skills, weights.experience, weights.location, weights.salary) == (40, 30, 15, 15)
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()
