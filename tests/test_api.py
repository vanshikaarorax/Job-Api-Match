def candidate_payload() -> dict:
    return {
        "name": "Vanshika",
        "skills": ["Python", " FastAPI "],
        "yearsOfExperience": 2,
        "location": "Delhi",
        "expectedSalary": 1200000,
    }


def job_payload() -> dict:
    return {
        "title": "ML Engineer",
        "requiredSkills": [{"name": "Python", "type": "must_have"}, {"name": "PyTorch", "type": "nice_to_have"}],
        "minYearsExperience": 2,
        "location": "Bangalore",
        "salaryRange": {"min": 1000000, "max": 1600000},
        "remoteAllowed": True,
    }


def test_create_candidate(client):
    response = client.post("/candidates", json=candidate_payload())
    assert response.status_code == 201
    assert response.json() == {
        "id": 1, "name": "Vanshika", "skills": ["python", "fastapi"],
        "yearsOfExperience": 2.0, "location": "Delhi", "expectedSalary": 1200000.0,
        "createdAt": response.json()["createdAt"],
    }


def test_create_job(client):
    response = client.post("/jobs", json=job_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "ML Engineer"
    assert body["requiredSkills"] == [{"name": "python", "type": "must_have"}, {"name": "pytorch", "type": "nice_to_have"}]
    assert body["salaryRange"] == {"min": 1000000.0, "max": 1600000.0}


def test_invalid_candidate_data(client):
    payload = candidate_payload()
    payload["skills"] = ["   "]
    response = client.post("/candidates", json=payload)
    assert response.status_code == 422


def test_invalid_job_salary_range(client):
    payload = job_payload()
    payload["salaryRange"] = {"min": 1600000, "max": 1000000}
    response = client.post("/jobs", json=payload)
    assert response.status_code == 422


def test_nonexistent_candidate_returns_404(client):
    response = client.get("/candidates/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate not found"


def test_nonexistent_job_returns_404(client):
    response = client.get("/jobs/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_recommendations_rank_then_apply_limit(client):
    candidate = client.post("/candidates", json=candidate_payload()).json()
    higher_ranked = job_payload()
    higher_ranked["title"] = "Perfect fit"
    higher_ranked["requiredSkills"] = [{"name": "Python", "type": "must_have"}]
    higher_ranked["location"] = "Delhi"
    higher_ranked["salaryRange"] = {"min": 1200000, "max": 1500000}
    lower_ranked = job_payload()
    lower_ranked["title"] = "Remote partial fit"
    lower_ranked["salaryRange"] = {"min": 1000000, "max": 1600000}
    client.post("/jobs", json=lower_ranked)
    client.post("/jobs", json=higher_ranked)
    excluded = job_payload()
    excluded["title"] = "Excluded despite other fit"
    excluded["requiredSkills"] = [{"name": "Rust", "type": "must_have"}]
    excluded["location"] = "Delhi"
    excluded["salaryRange"] = {"min": 2000000, "max": 3000000}
    client.post("/jobs", json=excluded)

    response = client.get(f"/candidates/{candidate['id']}/recommendations?limit=1")
    assert response.status_code == 200
    assert response.json()["candidateId"] == candidate["id"]
    assert response.json()["results"] == [{
        "jobId": 2, "title": "Perfect fit", "score": 100.0,
        "breakdown": {
            "skills": {"score": 50.0, "max": 50.0, "mustHave": {"matched": 1, "total": 1}, "niceToHave": {"matched": 0, "total": 0}},
            "experience": {"score": 20.0, "max": 20.0},
            "location": {"score": 15.0, "max": 15.0, "reason": "exact_match"},
            "salary": {"score": 15.0, "max": 15.0},
        },
    }]


def test_recommendations_missing_candidate_returns_404(client):
    response = client.get("/candidates/999/recommendations")
    assert response.status_code == 404


def test_recommendations_limit_is_validated(client):
    candidate = client.post("/candidates", json=candidate_payload()).json()
    assert client.get(f"/candidates/{candidate['id']}/recommendations?limit=0").status_code == 422


def test_job_recommendations_reuses_hard_filter_and_ranking(client):
    matching_candidate = client.post("/candidates", json=candidate_payload()).json()
    unmatched_payload = candidate_payload()
    unmatched_payload["name"] = "No Python"
    unmatched_payload["skills"] = ["Java"]
    client.post("/candidates", json=unmatched_payload)
    posting = job_payload()
    posting["requiredSkills"] = [{"name": "Python", "type": "must_have"}]
    posting["location"] = "Delhi"
    posting["salaryRange"] = {"min": 1200000, "max": 1500000}
    job = client.post("/jobs", json=posting).json()

    response = client.get(f"/jobs/{job['id']}/recommendations?limit=10")
    assert response.status_code == 200
    assert response.json()["jobId"] == job["id"]
    assert [result["candidateId"] for result in response.json()["results"]] == [matching_candidate["id"]]
    assert response.json()["results"][0]["score"] == 100


def test_job_recommendations_nonexistent_job_returns_404(client):
    assert client.get("/jobs/999/recommendations").status_code == 404
