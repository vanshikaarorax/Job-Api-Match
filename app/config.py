from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.scoring.config import ScoringWeights


class Settings(BaseSettings):
    """Application configuration sourced from the environment."""

    database_url: str = "postgresql+psycopg://localhost:5432/job_match"
    scoring_skills_weight: float = 50.0
    scoring_experience_weight: float = 20.0
    scoring_location_weight: float = 15.0
    scoring_salary_weight: float = 15.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_scoring_weights() -> ScoringWeights:
    settings = get_settings()
    return ScoringWeights(
        skills=settings.scoring_skills_weight,
        experience=settings.scoring_experience_weight,
        location=settings.scoring_location_weight,
        salary=settings.scoring_salary_weight,
    )
