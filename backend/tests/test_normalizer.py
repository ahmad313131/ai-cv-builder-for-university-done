from app.skill_normalize import SkillNormalizer

def test_normalizer_lists(tmp_path):
    # ملف skills_ontology.json موجود عندك – هون بنحاكيه مختصر
    data = {
        "skills": [
            {"canonical": "React", "aliases": ["react.js","reactjs"], "category": "frontend", "tags":[]},
            {"canonical": "Express", "aliases": ["express.js"], "category": "backend", "tags":[]}
        ],
        "families": {"frontend":["React"], "backend":["Express"]}
    }
    p = tmp_path/"skills_ontology.json"
    p.write_text(__import__("json").dumps(data))
    n = SkillNormalizer(str(p), threshold=0.5)

    user = n.normalize_list(["reactjs", "Express"])
    assert "React" in user and "Express" in user
    cats = n.categories(user)
    assert "frontend" in cats or "backend" in cats
