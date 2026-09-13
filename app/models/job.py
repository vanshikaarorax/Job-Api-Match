import enum
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class SkillType(str, enum.Enum):
    MUST_HAVE = "must_have"
    NICE_TO_HAVE = "nice_to_have"


def _skill_type_values(enum_class: type[SkillType]) -> list[str]:
    """Persist enum values, matching the lowercase PostgreSQL enum migration."""
    return [member.value for member in enum_class]


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="title_not_empty"),
        CheckConstraint("min_years_experience >= 0", name="min_years_non_negative"),
        CheckConstraint("salary_min >= 0", name="salary_min_non_negative"),
        CheckConstraint("salary_max >= salary_min", name="salary_range_valid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    min_years_experience: Mapped[float] = mapped_column(Float, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    salary_min: Mapped[float] = mapped_column(Float, nullable=False)
    salary_max: Mapped[float] = mapped_column(Float, nullable=False)
    remote_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    required_skills: Mapped[list["JobSkill"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", lazy="selectin"
    )


class JobSkill(Base):
    __tablename__ = "job_skills"
    __table_args__ = (CheckConstraint("length(trim(skill_name)) > 0", name="skill_not_empty"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    skill_type: Mapped[SkillType] = mapped_column(
        Enum(SkillType, name="skill_type", values_callable=_skill_type_values), nullable=False
    )
    job: Mapped[Job] = relationship(back_populates="required_skills")
