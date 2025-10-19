# app/ai_llm.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import requests, os, json
from .schemas import CVIn
from .skill_normalize import SkillNormalizer


router = APIRouter()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1:latest")

normalizer = SkillNormalizer("data/skills_ontology.json", threshold=0.46)

class LLMAnalysisOut(BaseModel):
    matching_score: float
    match_level: str
    reasons: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    nice_to_have: list[str] = Field(default_factory=list)

SYSTEM_PROMPT = """
You are an explainer. Given canonical skills for USER and JD and an initial score and suggestions,
return JSON ONLY with keys: matching_score, match_level, reasons (2–5 concise bullets),
missing_skills (concrete skills absent in USER but present/expected in JD canonical set),
nice_to_have (0–6).
- Always return JSON arrays of strings for "reasons", "missing_skills", and "nice_to_have".
- Do NOT change 'matching_score' or 'match_level' unless inputs are inconsistent.
- Use only the canonical names provided.
Return valid JSON only.
"""

def judge_level(score: float) -> str:
    return "Strong Match" if score >= 70 else "Medium Match" if score >= 40 else "Weak Match"

@router.post("/api/llm_analyze_cv", response_model=LLMAnalysisOut)
def llm_analyze_cv(payload: CVIn):
    skills_csv = payload.skills or ""
    jd_text    = getattr(payload, "job_description", "") or ""
    user_raw   = [s.strip() for s in skills_csv.split(",") if s.strip()]

    if not user_raw and not jd_text:
        raise HTTPException(status_code=400, detail="Provide skills and/or a job description.")

    # 1) Canonicalize
    user_can = normalizer.normalize_list(user_raw)
    jd_can   = normalizer.normalize_text(jd_text)
    overlap  = user_can & jd_can

    # 2) Deterministic score (not from LLM)
    cov     = len(overlap) / max(1, len(jd_can) or len(user_can))
    breadth = len(normalizer.categories(overlap)) / max(1, len(normalizer.categories(jd_can)) or 1)
    score   = (0.7 * cov + 0.3 * breadth) * 100

    if {"React"} & jd_can and {"React"} & user_can and {"Node.js","Express"} & user_can:
        score = max(score, 90)

    score = round(min(96.0, max(0.0, score)), 2)
    level = judge_level(score)

    missing = sorted(list(jd_can - user_can))[:10]

    nice_seed = []
    if "React" in jd_can and "TypeScript" not in user_can and "TypeScript" not in jd_can:
        nice_seed.append("TypeScript")
    if "PostgreSQL" not in user_can and "PostgreSQL" not in jd_can and "MongoDB" not in user_can:
        nice_seed.append("PostgreSQL")
    if "Docker" not in user_can and "Docker" not in jd_can:
        nice_seed.append("Docker")
    nice_seed = nice_seed[:6]

    user_msg = json.dumps({
        "user_canonical": sorted(list(user_can)),
        "jd_canonical": sorted(list(jd_can)),
        "overlap": sorted(list(overlap)),
        "initial_score": score,
        "initial_level": level,
        "suggestions": missing,
        "nice_seed": nice_seed
    })

    payload_llm = {
        "model": MODEL_NAME,
        "format": "json",
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        "options": {"temperature": 0.0, "num_predict": 384}
    }

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload_llm,
            headers={"Accept": "application/json"},
            timeout=120
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Ollama connection error: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Ollama error {resp.status_code}: {resp.text}")

    text = resp.text.strip()
    try:
        data = resp.json()
    except Exception:
        # NDJSON fallback
        objs = []
        for line in text.splitlines():
            line = line.strip()
            if not line: continue
            try: objs.append(json.loads(line))
            except: pass
        if not objs:
            raise HTTPException(status_code=502, detail="LLM returned non-JSON/NDJSON content.")
        data = objs[-1]

    content = ((data.get("message") or {}).get("content") or (data.get("response") or "")).strip()
    if not content:
        raise HTTPException(status_code=502, detail="Empty response from LLM.")

    # Parse JSON content
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise HTTPException(status_code=502, detail="LLM returned non-JSON content in message.")
        parsed = json.loads(content[start:end+1])

    def as_list(x):
        if isinstance(x, list): return [str(i) for i in x]
        if x is None: return []
        if isinstance(x, (int, float)): return [str(x)]
        if isinstance(x, str):
            try:
                j = json.loads(x)
                if isinstance(j, list): return [str(i) for i in j]
            except Exception:
                pass
            return [s.strip() for s in x.split(",") if s.strip()]
        return [str(x)]

    out_score = score
    out_level = level
    reasons   = as_list(parsed.get("reasons"))[:5]
    missing_skills = missing

    nice_llm_list  = as_list(parsed.get("nice_to_have"))
    nice_llm_norm  = normalizer.normalize_list(nice_llm_list)
    nice_seed_norm = set(nice_seed)
    nice_union     = (nice_llm_norm | nice_seed_norm) - user_can - jd_can
    nice_to_have   = sorted(list(nice_union))[:10]

    return LLMAnalysisOut(
        matching_score=round(out_score, 2),
        match_level=out_level,
        reasons=reasons,
        missing_skills=missing_skills,
        nice_to_have=nice_to_have,
    )

# =========================
# Polisher (dynamic buckets)
# =========================

POLISH_SYSTEM = (
    "You are a professional resume writer. Output VALID JSON only. "
    "Make the CV concise, ATS-friendly, and professional. "
    "Profile (professional_summary) should be a 2–3-sentence summary highlighting role, tech stack, and achievements. "
    "Work experience bullets should start with strong action verbs (Developed, Built, Designed, Implemented, etc.) "
    "and describe what was achieved or improved. "
    "Avoid repeating the same phrases between profile and experience. "
    "Education should be clear, e.g. 'B.Sc. in Computer Science — LIU (2022–2025)'. "
    "Group skills into up to 25 meaningful categories. "
    "Do NOT invent facts or companies not in input. "
    "Return valid JSON only."
)


def polish_cv_struct(cv: CVIn) -> dict:
    """Call Ollama to produce a polished CV structure with dynamic skill categories."""
    import json, re, hashlib
    import requests
    from fastapi import HTTPException

    # 0) تحضير الدخل
    payload_user = {
        "cv_in": {
            "name": cv.name, "email": str(cv.email),
            "education": cv.education or "",
            "experience": cv.experience or "",
            "skills": cv.skills or "",
            "github": cv.github or "", "linkedin": cv.linkedin or "",
            "languages": cv.languages or "", "hobbies": cv.hobbies or ""
        }
    }

    user_prompt = {
        "instruction": "Return JSON ONLY with these keys.",
        "schema": {
            "name": "string",
            "title": "string",
            "professional_summary": "string",
            "key_skills": {"<dynamic_category>": ["string"]},  # up to 25 categories
            "key_skills_flat": ["string"],                     # union of all categories (deduped)
            "experience_bullets": ["string"],
            "education_section": ["string"],
            "links": {"github": "string", "linkedin": "string", "email": "string"},
            "languages": ["string"],
            "hobbies": ["string"]
        },
        "rules": [
            "Use only info present in input. No new tech or facts.",
            "Max 25 categories in key_skills; omit empty categories.",
            "Bullets are crisp (≤ 2 lines), no first-person.",
            "key_skills_flat = union of all category arrays, unique, compact."
        ],
        "input": payload_user
    }

    body = {
        "model": MODEL_NAME,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.0, "seed": 42, "num_predict": 768},
        "messages": [
            {"role": "system", "content": POLISH_SYSTEM},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
        ]
    }

    # 1) نداء Ollama ثم Parse آمن
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=120)
        r.raise_for_status()
        data = r.json()
        content = ((data.get("message") or {}).get("content") or (data.get("response") or "")).strip()
        try:
            out = json.loads(content)
        except json.JSONDecodeError:
            s, e = content.find("{"), content.rfind("}")
            if s == -1 or e == -1 or e <= s:
                raise HTTPException(status_code=502, detail="Polish LLM returned non-JSON.")
            out = json.loads(content[s:e+1])
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Ollama connection error: {e}")

    # 2) Sanitize / تطبيع الحقول
    def _arr(x):
        if isinstance(x, list): return [str(i) for i in x][:100]
        if isinstance(x, str):  return [i.strip() for i in x.split(",") if i.strip()][:100]
        return []

    # key_skills (قاموس ديناميكي) + flat
    ks = out.get("key_skills") or {}
    if not isinstance(ks, dict): ks = {}
    keys = list(ks.keys())[:25]
    ks = {k: _arr(ks.get(k)) for k in keys}
    flat = out.get("key_skills_flat")
    if not flat:
        seen = set(); flat_list = []
        for arr in ks.values():
            for s in arr:
                if s and s not in seen:
                    seen.add(s); flat_list.append(s)
        flat = flat_list[:150]
    else:
        flat = _arr(flat)

    out["key_skills"] = ks
    out["key_skills_flat"] = flat
    out["experience_bullets"] = _arr(out.get("experience_bullets"))
    out["education_section"]  = _arr(out.get("education_section"))
    out["languages"] = _arr(out.get("languages"))
    out["hobbies"]   = _arr(out.get("hobbies"))

    links = out.get("links") or {}
    if not isinstance(links, dict): links = {}
    links.setdefault("email", str(cv.email))
    links.setdefault("github", cv.github or "")
    links.setdefault("linkedin", cv.linkedin or "")
    out["links"] = links

    if not out.get("title"):
        out["title"] = "Software Engineer"
    if not out.get("name"):
        out["name"] = cv.name

    # 3) تحسين رصاصات الخبرة بأفعال مناسبة للدومين (من JSON خارجي إن وُجد، وإلا فولباك عام)
    try:
        from .utils_actions import (
            load_action_config, infer_domains, build_verb_pool,
            starts_with_verb, pick_verb_deterministic
        )
        # اجمع نص مهارات شامل من polished + payload
        def _skill_text(polished_obj: dict, payload_obj: 'CVIn') -> str:
            parts = []
            _ks = polished_obj.get("key_skills") or {}
            if isinstance(_ks, dict):
                for cat, arr in _ks.items():
                    parts.append(str(cat)); parts.extend([str(x) for x in (arr or [])])
            parts.extend(polished_obj.get("key_skills_flat") or [])
            parts.append(payload_obj.skills or "")
            return " ".join([p.lower() for p in parts if p])

        skill_text = _skill_text(out, cv)
        _cfg = load_action_config()
        _domains = infer_domains(skill_text, _cfg)
        _pool = build_verb_pool(_domains, _cfg)

        polished_bullets = []
        for b in out["experience_bullets"]:
            b = (b or "").strip()
            if not b: 
                continue
            b = b[0].upper() + b[1:]
            b = b.rstrip(". ")
            words = b.split()
            needs_verb = (len(words) < 5) or (not starts_with_verb(b, _cfg))
            if needs_verb:
                b_no_bullet = re.sub(r"^[•\-\s]+", "", b)
                if not starts_with_verb(b_no_bullet, _cfg):
                    verb = pick_verb_deterministic(b_no_bullet, _pool)
                    b = f"{verb} {b_no_bullet[0].lower()+b_no_bullet[1:] if b_no_bullet else ''}"
            polished_bullets.append(b)

        out["experience_bullets"] = polished_bullets[:12]

    except Exception:
        # فولباك بسيط إذا ما في utils_actions أو JSON
        DEFAULT_VERBS = ["Developed","Implemented","Built","Created","Designed","Engineered","Optimized","Integrated","Deployed"]
        def starts_with_any(line: str) -> bool:
            if not line: return False
            first = re.split(r"\s+", line.strip())[0].lower().strip("•-:")
            return first in {v.lower() for v in DEFAULT_VERBS}

        def pick_verb(text: str) -> str:
            h = hashlib.md5((text or "").strip().encode("utf-8")).hexdigest()
            return DEFAULT_VERBS[int(h[:8], 16) % len(DEFAULT_VERBS)]

        bullets = []
        for b in out["experience_bullets"]:
            b = (b or "").strip()
            if not b: 
                continue
            b = b[0].upper() + b[1:]
            b = b.rstrip(". ")
            if (len(b.split()) < 5) or (not starts_with_any(b)):
                core = re.sub(r"^[•\-\s]+", "", b)
                if not starts_with_any(core):
                    b = f"{pick_verb(core)} {core[0].lower()+core[1:] if core else ''}"
            bullets.append(b)
        out["experience_bullets"] = bullets[:12]

    return out
