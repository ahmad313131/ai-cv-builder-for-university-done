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

# ------- Missing skills: same-category prioritization -------
from collections import defaultdict

def pick_missing_same_category(jd_set: set[str],
                               user_set: set[str],
                               per_cat: int = 3,
                               total: int = 10) -> list[str]:
    """
    Return missing skills from JD (jd_set - user_set), prioritized by categories:
      1) Categories that the user already has (intersection of user_cats & jd_cats).
      2) Then the remaining JD categories.
    Deterministic ordering: sort categories and skills alphabetically within buckets.
    """
    # missing universe
    missing_all = (jd_set - user_set)
    if not missing_all:
        return []

    # group missing by category
    by_cat = defaultdict(list)
    for s in missing_all:
        by_cat[normalizer.category(s)].append(s)
    for cat in by_cat:
        by_cat[cat] = sorted(set(by_cat[cat]))  # stable & dedup

    # compute category priorities
    user_cats = normalizer.categories(user_set)
    jd_cats   = normalizer.categories(jd_set)

    primary   = sorted((user_cats & jd_cats))      # shared categories first
    secondary = sorted((jd_cats - user_cats))      # then other JD cats

    ordered_cats = primary + secondary

    # round-robin pick with per-cat and total caps
    out = []
    for cat in ordered_cats:
        if len(out) >= total:
            break
        bucket = by_cat.get(cat, [])
        out.extend(bucket[:per_cat])
    return out[:total]
# ---------------------------------------------------#

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
    jd_core = jd_can

    # 2) F1/Dice-like coverage + category breadth (NO JD filtering)
    U = len(user_can)
    J = len(jd_can)
    O = len(overlap)

    coverage_user = O / max(1, U)
    coverage_jd   = O / max(1, J)
    coverage      = (coverage_user + coverage_jd) / 2.0

    cats_user = normalizer.categories(user_can)
    cats_jd   = normalizer.categories(jd_can)
    cats_ov   = normalizer.categories(overlap)

    Cu = len(cats_user)
    Cj = len(cats_jd)
    Co = len(cats_ov)

    breadth_user = Co / max(1, Cu)
    breadth_jd   = Co / max(1, Cj)
    breadth      = (breadth_user + breadth_jd) / 2.0

    score = (0.8 * coverage + 0.2 * breadth) * 100.0
    score = round(min(96.0, max(0.0, score)), 2)
    level = judge_level(score)

    # 3) Missing skills (from full JD)
    missing = pick_missing_same_category(
    jd_set=jd_core,
    user_set=user_can,
    per_cat=3,   # غيّرها إذا بدك
    total=10
)

    # 4) Nice-to-have = 3 max (ontology-guided, same JD categories)
    exclude   = user_can | jd_can
    nice_seed = normalizer.suggest_by_categories(
        categories=cats_jd,
        exclude=exclude,
        per_cat=2,
        total=3
    )

    # 5) Call LLM for explanations only (does not change score)
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

    reasons = as_list(parsed.get("reasons"))[:5]

    # Merge nice_to_have (LLM + seed), dedupe via ontology, clamp to 3
    nice_llm_list  = as_list(parsed.get("nice_to_have"))
    nice_llm_norm  = normalizer.normalize_list(nice_llm_list)
    nice_seed_norm = set(nice_seed)
    nice_union     = (nice_llm_norm | nice_seed_norm) - user_can - jd_can
    nice_to_have   = sorted(list(nice_union))[:3]

    return LLMAnalysisOut(
        matching_score=round(score, 2),
        match_level=level,
        reasons=reasons,
        missing_skills=missing,
        nice_to_have=nice_to_have,
    )


# =========================
# Polisher (dynamic buckets)
# =========================

POLISH_SYSTEM = (
    "You are a professional resume writer. Output VALID JSON only. "
    "Make the CV ATS-friendly and professional. "
    "Professional summary should be 3–5 sentences (~60–100 words) highlighting role, stack, scope, and quantifiable achievements. "
    "Work experience bullets can be 1–2 sentences each (up to ~30–35 words) and must start with strong action verbs "
    "(Developed, Built, Designed, Implemented, Optimized, Led, Architected, Automated, etc.). "
    "Bullets should include impact, scale, metrics, or business value when possible. "
    "Avoid repeating phrases between profile and bullets. "
    "Education should be clear (e.g., 'B.Sc. in Computer Science — LIU (2022–2025)'). "
    "Group skills into up to 25 meaningful categories. "
    "Use only info present in input (no invented facts or companies). "
    "Return valid JSON only."
)

def polish_cv_struct(cv: CVIn) -> dict:
    """Call Ollama to produce a polished CV structure with dynamic skill categories."""
    import json, re, hashlib, os
    import requests
    from fastapi import HTTPException

    # 0) Prepare input
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
            "key_skills": {"<dynamic_category>": ["string"]},
            "key_skills_flat": ["string"],
            "experience_bullets": ["string"],
            "education_section": ["string"],
            "links": {"github": "string", "linkedin": "string", "email": "string"},
            "languages": ["string"],
            "hobbies": ["string"]
        },
        "rules": [
            "Use only info present in input. No new tech or facts.",
            "Professional summary: 3–5 sentences (~60–100 words).",
            "Bullets: 1–2 sentences, up to ~30–35 words each, start with a strong action verb.",
            "Max 25 categories in key_skills; omit empty categories.",
            "key_skills_flat = union of all category arrays, unique, compact."
        ],
        "input": payload_user
    }

    body = {
        "model": MODEL_NAME,
        "format": "json",
        "stream": False,
        # نرفع سقف التوقّعات ليفسح مجال لنص أطول
        "options": {"temperature": 0.0, "seed": 42, "num_predict": 1200},
        "messages": [
            {"role": "system", "content": POLISH_SYSTEM},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
        ]
    }

    # 1) Call Ollama + safe parse
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

    # 2) Sanitize / normalize arrays (قابلة للتهيئة عبر ENV)
    def _arr(x):
        if isinstance(x, list): return [str(i) for i in x][:300]
        if isinstance(x, str):  return [i.strip() for i in x.split(",") if i.strip()][:300]
        return []

    MAX_BULLETS      = int(os.getenv("POLISH_MAX_BULLETS", "18"))
    MAX_EDU          = int(os.getenv("POLISH_MAX_EDU_ITEMS", "8"))
    MAX_SKILLS_FLAT  = int(os.getenv("POLISH_MAX_SKILLS_FLAT", "200"))

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
        flat = flat_list[:MAX_SKILLS_FLAT]
    else:
        flat = _arr(flat)[:MAX_SKILLS_FLAT]

    out["key_skills"] = ks
    out["key_skills_flat"] = flat
    out["experience_bullets"] = _arr(out.get("experience_bullets"))[:MAX_BULLETS]
    out["education_section"]  = _arr(out.get("education_section"))[:MAX_EDU]
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

    # 3) Optional: improve bullets with action verbs (kept as in your original, مع احترام الحد الجديد)
    try:
        from .utils_actions import (
            load_action_config, infer_domains, build_verb_pool,
            starts_with_verb, pick_verb_deterministic
        )

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

        # احترم الحد الجديد بدل 12 الثابت
        out["experience_bullets"] = polished_bullets[:MAX_BULLETS]

    except Exception:
        DEFAULT_VERBS = ["Developed","Implemented","Built","Created","Designed","Engineered","Optimized","Integrated","Deployed"]
        def starts_with_any(line: str) -> bool:
            if not line: return False
            first = re.split(r"\s+", line.strip())[0].lower().strip("•-:")
            return first in {v.lower() for v in DEFAULT_VERBS}
        def pick_verb(text: str) -> str:
            h = hashlib.md5((text or "").strip().encode("utf-8")).hexdigest()
            return DEFAULT_VERBS[int(h[:8], 16) % len(DEFAULT_VERBS)]

        bullets = []
        for b in out.get("experience_bullets", []):
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

        out["experience_bullets"] = bullets[:MAX_BULLETS]

    return out
