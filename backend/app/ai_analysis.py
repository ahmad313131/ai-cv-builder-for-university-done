# app/ai_analysis.py
from fastapi import APIRouter
from app.main import CVIn
from .schemas import CVIn
from .skill_normalize import SkillNormalizer

import os

router = APIRouter()

# حمّل النورمالايزر (بيعتمد على data/skills_ontology.json)
normalizer = SkillNormalizer("data/skills_ontology.json", threshold=0.46)

def _label(score: float) -> str:
    if score >= 70:
        return "Strong Match"
    if score >= 40:
        return "Medium Match"
    return "Weak Match"

@router.post("/api/analyze_cv")
def analyze_cv(payload: CVIn):
    """تحليل بسيط وواقعي باستخدام قاموس مهارات مُوحّد (canonical)."""
    # 1) قراءة المدخلات
    user_raw = [s.strip() for s in (payload.skills or "").split(",") if s.strip()]
    jd_text  = (getattr(payload, "job_description", "") or "").strip()

    if not user_raw and not jd_text:
        return {
            "matching_score": 0.0,
            "match_level": "Weak Match",
            "suggestions": [],
            "note": "Please add skills and/or a job description."
        }

    # 2) تطبيع المهارات إلى أسماء canonical
    user_can = normalizer.normalize_list(user_raw)   # set[str]
    jd_can   = normalizer.normalize_text(jd_text)    # set[str]

    # 3) سكّور واقعي: تغطية + عرض فئات
    overlap = user_can & jd_can
    cov = len(overlap) / max(1, len(jd_can) or len(user_can))
    breadth = len(normalizer.categories(overlap)) / max(1, len(normalizer.categories(jd_can)) or 1)

    score = (0.7 * cov + 0.3 * breadth) * 100.0

    # إذا الـJD فيها Backend والمستخدم ما عنده أي Backend → سقّف 75
    jd_cats = normalizer.categories(jd_can)
    user_cats = normalizer.categories(user_can)
    jd_backend = "backend" in jd_cats
    user_backend = "backend" in user_cats
    if jd_backend and not user_backend:
        score = min(score, 75.0)

    # سقف عام 96 لتجنّب 100% المبالغ فيها
    score = round(min(96.0, max(0.0, score)), 2)

    # 4) الاقتراحات: فقط ما ينقص من الـJD
    suggestions = sorted(list(jd_can - user_can))[:10]

    resp = {
        "matching_score": score,
        "match_level": _label(score),
        "suggestions": suggestions
    }

    # Debug اختياري عبر ENV
    if os.getenv("DEBUG_ANALYZE") == "1":
        resp["debug"] = {
            "user_canonical": sorted(list(user_can)),
            "jd_canonical": sorted(list(jd_can)),
            "overlap": sorted(list(overlap)),
            "jd_categories": sorted(list(jd_cats)),
            "user_categories": sorted(list(user_cats)),
        }

    return resp
