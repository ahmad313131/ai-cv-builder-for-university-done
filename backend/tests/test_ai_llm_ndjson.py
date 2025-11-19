# tests/test_ai_llm_ndjson.py
import app.ai_llm as ai_llm
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_llm_analyze_cv_ndjson(monkeypatch):
    class NDJSONResp:
        status_code = 200
        # لنجبر الكود يقرأ .text ويعمل fallback سطور NDJSON
        text = '\n'.join([
            '{"message":{"content":"{ \\"matching_score\\": 65, \\"match_level\\": \\"Medium Match\\", '
            '\\"reasons\\":[\\"ok\\"], \\"missing_skills\\":[\\"Node.js\\"], \\"nice_to_have\\":[\\"Redux\\"] }"}}'
        ])
        def json(self):  # نخليها تفشل عمداً ليروح على fallback
            raise ValueError("force text path")
    monkeypatch.setattr(ai_llm.requests, "post", lambda *a, **k: NDJSONResp())
    payload = {"name":"A","email":"a@a.com","skills":"React, Express","job_description":"React backend"}
    r = client.post("/api/llm_analyze_cv", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "matching_score" in body and "reasons" in body
