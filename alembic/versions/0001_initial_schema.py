"""create initial job match schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-13
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

skill_type = sa.Enum("must_have", "nice_to_have", name="skill_type")


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("years_of_experience", sa.Float(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("expected_salary", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_candidates_name_not_empty"),
        sa.CheckConstraint("years_of_experience >= 0", name="ck_candidates_years_non_negative"),
        sa.CheckConstraint("expected_salary >= 0", name="ck_candidates_salary_non_negative"),
        sa.PrimaryKeyConstraint("id", name="pk_candidates"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("min_years_experience", sa.Float(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("salary_min", sa.Float(), nullable=False),
        sa.Column("salary_max", sa.Float(), nullable=False),
        sa.Column("remote_allowed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_jobs_title_not_empty"),
        sa.CheckConstraint("min_years_experience >= 0", name="ck_jobs_min_years_non_negative"),
        sa.CheckConstraint("salary_min >= 0", name="ck_jobs_salary_min_non_negative"),
        sa.CheckConstraint("salary_max >= salary_min", name="ck_jobs_salary_range_valid"),
        sa.PrimaryKeyConstraint("id", name="pk_jobs"),
    )
    op.create_table(
        "candidate_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("skill_name", sa.String(length=255), nullable=False),
        sa.CheckConstraint("length(trim(skill_name)) > 0", name="ck_candidate_skills_skill_not_empty"),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], name="fk_candidate_skills_candidate_id_candidates", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_candidate_skills"),
    )
    op.create_index("ix_candidate_skills_candidate_id", "candidate_skills", ["candidate_id"])
    op.create_table(
        "job_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("skill_name", sa.String(length=255), nullable=False),
        sa.Column("skill_type", skill_type, nullable=False),
        sa.CheckConstraint("length(trim(skill_name)) > 0", name="ck_job_skills_skill_not_empty"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], name="fk_job_skills_job_id_jobs", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_job_skills"),
    )
    op.create_index("ix_job_skills_job_id", "job_skills", ["job_id"])


def downgrade() -> None:
    op.drop_index("ix_job_skills_job_id", table_name="job_skills")
    op.drop_table("job_skills")
    op.drop_index("ix_candidate_skills_candidate_id", table_name="candidate_skills")
    op.drop_table("candidate_skills")
    op.drop_table("jobs")
    op.drop_table("candidates")
