from fastapi import FastAPI

from app.api.routes import candidates, job_recommendations, jobs, recommendations

app = FastAPI(title="Job Match API", version="0.1.0")
app.include_router(candidates.router)
app.include_router(jobs.router)
app.include_router(recommendations.router)
app.include_router(job_recommendations.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
