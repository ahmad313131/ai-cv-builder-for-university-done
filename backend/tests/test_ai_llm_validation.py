# tests/test_ai_llm_validation.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_llm_analyze_cv_validation_error():
    r = client.post("/api/llm_analyze_cv", json={"skills": "", "job_description": ""})
    assert r.status_code == 422
    assert "Provide skills" in r.text
