# tests/test_ai_llm_error_paths.py
import app.ai_llm as ai_llm
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_llm_analyze_cv_ollama_non_200(monkeypatch):
    class BadResp:
        status_code = 500
        text = "server error"
        def json(self): return {}
    monkeypatch.setattr(ai_llm.requests, "post", lambda *a, **k: BadResp())
    payload = {"name":"A","email":"a@a.com","skills":"React","job_description":"React dev"}
    r = client.post("/api/llm_analyze_cv", json=payload)
    assert r.status_code == 502
    assert "Ollama error 500" in r.text
