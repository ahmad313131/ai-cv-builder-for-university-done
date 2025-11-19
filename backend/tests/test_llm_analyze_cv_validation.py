from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# tests/test_llm_analyze_cv_validation.py
def test_llm_analyze_cv_validation_error():
    r = client.post("/api/llm_analyze_cv", json={
        "name": "Test",
        "email": "t@t.com",
        "skills": "",
        "job_description": ""
    })
    assert r.status_code == 400
    assert r.json()["detail"] == "Provide skills and/or a job description."

