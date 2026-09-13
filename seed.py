"""Reset and populate the configured database with deterministic demo data.

Run `alembic upgrade head` first. This script intentionally replaces existing
candidates and jobs, making repeated local demos reproducible.
"""

from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models.candidate import Candidate, CandidateSkill
from app.models.job import Job, JobSkill, SkillType


CANDIDATES = [
    ("Aarav Sharma", ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"], 4, "Bangalore", 1800000),
    ("Meera Iyer", ["Python", "PyTorch", "TensorFlow", "Pandas", "SQL"], 3, "Delhi", 1600000),
    ("Rohan Kapoor", ["Python", "OpenCV", "PyTorch", "CUDA", "Docker"], 2, "Hyderabad", 1400000),
    ("Ananya Gupta", ["Python", "Pandas", "SQL", "scikit-learn", "Tableau"], 4, "Mumbai", 1700000),
    ("Kabir Singh", ["Python", "Django", "FastAPI", "Redis", "PostgreSQL"], 1, "Pune", 1000000),
    ("Ishita Rao", ["Python", "Kubernetes", "Docker", "AWS", "MLflow"], 5, "Bangalore", 2200000),
    ("Vikram Nair", ["Python", "PyTorch", "Transformers", "NLP", "Research"], 6, "Chennai", 2500000),
    ("Sara Khan", ["Python", "React", "TypeScript", "FastAPI", "PostgreSQL"], 3, "Delhi", 1500000),
]

JOBS = [
    ("Backend Engineer", [("Python", "must_have"), ("FastAPI", "must_have"), ("Docker", "nice_to_have")], 3, "Bangalore", 1400000, 2000000, False),
    ("Senior Backend Engineer", [("Python", "must_have"), ("PostgreSQL", "must_have"), ("Kubernetes", "nice_to_have")], 6, "Bangalore", 2200000, 3000000, False),
    ("FastAPI Developer", [("Python", "must_have"), ("FastAPI", "must_have")], 0, "Delhi", 900000, 1500000, True),
    ("ML Engineer", [("Python", "must_have"), ("PyTorch", "must_have"), ("MLflow", "nice_to_have")], 3, "Delhi", 1400000, 2100000, True),
    ("Senior ML Engineer", [("Python", "must_have"), ("TensorFlow", "must_have"), ("Kubernetes", "nice_to_have")], 6, "Bangalore", 2300000, 3200000, False),
    ("Computer Vision Engineer", [("Python", "must_have"), ("OpenCV", "must_have"), ("CUDA", "nice_to_have")], 3, "Hyderabad", 1200000, 1800000, False),
    ("AI Engineer", [("Python", "must_have"), ("PyTorch", "nice_to_have"), ("Transformers", "nice_to_have")], 2, "Chennai", 1500000, 2400000, True),
    ("Data Scientist", [("Python", "must_have"), ("SQL", "must_have"), ("Tableau", "nice_to_have")], 3, "Mumbai", 1300000, 1900000, False),
    ("Data Analyst", [("SQL", "must_have"), ("Tableau", "must_have"), ("Python", "nice_to_have")], 1, "Pune", 800000, 1200000, True),
    ("MLOps Engineer", [("Python", "must_have"), ("Docker", "must_have"), ("Kubernetes", "must_have"), ("AWS", "nice_to_have")], 4, "Bangalore", 2000000, 2800000, False),
    ("Python Developer", [("Python", "must_have"), ("Django", "nice_to_have")], 1, "Pune", 900000, 1300000, True),
    ("NLP Engineer", [("Python", "must_have"), ("Transformers", "must_have"), ("NLP", "must_have")], 4, "Chennai", 2200000, 3000000, True),
    ("Deep Learning Engineer", [("Python", "must_have"), ("PyTorch", "must_have"), ("CUDA", "nice_to_have")], 5, "Hyderabad", 1800000, 2600000, False),
    ("Research Engineer", [("Python", "must_have"), ("Research", "must_have"), ("PyTorch", "nice_to_have")], 5, "Chennai", 2400000, 3500000, True),
    ("Platform Engineer", [("Go", "must_have"), ("Kubernetes", "must_have")], 4, "Bangalore", 1800000, 2600000, False),
    ("Frontend Engineer", [("React", "must_have"), ("TypeScript", "must_have"), ("Python", "nice_to_have")], 3, "Delhi", 1300000, 1800000, False),
    ("Junior Backend Engineer", [("Python", "must_have"), ("PostgreSQL", "nice_to_have")], 0, "Mumbai", 700000, 1000000, True),
    ("Applied Scientist", [("Python", "must_have"), ("PyTorch", "must_have"), ("Statistics", "nice_to_have")], 3, "Bangalore", 1000000, 1500000, True),
    ("Cloud Backend Engineer", [("Python", "must_have"), ("AWS", "must_have"), ("FastAPI", "nice_to_have")], 5, "Bangalore", 2500000, 3200000, False),
    ("Data Platform Engineer", [("Python", "must_have"), ("SQL", "must_have"), ("Airflow", "must_have")], 4, "Mumbai", 1500000, 2300000, False),
    ("AI Intern", [("Python", "must_have")], 0, "Delhi", 300000, 600000, False),
    ("Remote Python Consultant", [("Python", "must_have"), ("FastAPI", "nice_to_have")], 2, "Remote", 1600000, 2400000, True),
    ("Vision Researcher", [("Python", "must_have"), ("OpenCV", "must_have"), ("PyTorch", "must_have")], 4, "Bangalore", 1600000, 2100000, True),
    ("Analytics Engineer", [("SQL", "must_have"), ("dbt", "must_have"), ("Python", "nice_to_have")], 3, "Mumbai", 1400000, 2000000, False),
    ("API Engineer", [("Python", "must_have"), ("FastAPI", "must_have"), ("Redis", "nice_to_have")], 2, "Pune", 1100000, 1700000, False),
]


def seed() -> None:
    with SessionLocal() as db:
        db.execute(delete(Job))
        db.execute(delete(Candidate))
        db.flush()
        for name, skills, years, location, expected_salary in CANDIDATES:
            db.add(Candidate(name=name, years_of_experience=years, location=location, expected_salary=expected_salary,
                             skills=[CandidateSkill(skill_name=skill.casefold()) for skill in skills]))
        for title, requirements, years, location, salary_min, salary_max, remote_allowed in JOBS:
            db.add(Job(title=title, min_years_experience=years, location=location, salary_min=salary_min,
                       salary_max=salary_max, remote_allowed=remote_allowed,
                       required_skills=[JobSkill(skill_name=name.casefold(), skill_type=SkillType(skill_type)) for name, skill_type in requirements]))
        db.commit()
    print(f"Seeded {len(CANDIDATES)} candidates and {len(JOBS)} jobs.")


if __name__ == "__main__":
    seed()
