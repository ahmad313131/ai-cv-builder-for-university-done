# tests/test_ai_llm_pick_missing.py
from app.ai_llm import pick_missing_same_category, normalizer

def test_pick_missing_same_category_basic():
    jd = normalizer.normalize_list(["React", "Node.js", "Redis"])
    user = normalizer.normalize_list(["React"])
    out = pick_missing_same_category(jd, user, per_cat=2, total=5)
    assert isinstance(out, list)
    # لازم يكون في شي ناقص من JD مش عند اليوزر
    assert set(out).issubset(jd - user)
