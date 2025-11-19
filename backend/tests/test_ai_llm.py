import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_llm_analyze_cv_success(monkeypatch):
    # رجّع رد LLM بشكل ثابت
    def fake_post(url, json=None, headers=None, timeout=120):
        import json as json_module
        class Resp:
            status_code = 200
            # FastAPI code sometimes reads .text then .json(), so provide both
            _payload = {
                "matching_score": 72.5,
                "match_level": "Strong Match",
                "reasons": ["Good overlap", "Relevant categories"],
                "missing_skills": ["Node.js"],
                "nice_to_have": ["Redux"]
            }
            text = json_module.dumps({"message": {"content": json_module.dumps(_payload)}})
            def json(self):
                return {"message": {"content": json_module.dumps(self._payload)}}
        return Resp()


    import app.ai_llm as ai_llm
    monkeypatch.setattr(ai_llm.requests, "post", fake_post)

    payload = {
        "name": "Alex",
        "email": "a@a.com",
        "skills": "React, Express",
        "job_description": "React developer with backend"
    }
    r = client.post("/api/llm_analyze_cv", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["matching_score"] >= 0
    assert isinstance(body["reasons"], list)

def test_llm_analyze_cv_bad_request():
    r = client.post("/api/llm_analyze_cv", json={"name":"x","email":"x@x.com"})
    assert r.status_code == 400
