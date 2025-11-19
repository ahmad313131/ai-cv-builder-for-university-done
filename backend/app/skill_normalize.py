# app/skill_normalize.py
import json, re
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer, util

_TOKEN = re.compile(r"[A-Za-z0-9+.#]+")

def _tok(s: str) -> str:
    return " ".join(_TOKEN.findall((s or "").lower()))

class SkillNormalizer:
    def __init__(self, ontology_path="data/skills_ontology.json", threshold=0.46):
        self.threshold = float(threshold)

        with open(ontology_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.specialties = data.get("specialties", {})
        # دعم خلفي: إذا الملف القديم كان list مباشرة
        skills = data.get("skills", data if isinstance(data, list) else [])
        self.family_keywords = { (k or "").lower(): set(v) for k, v in data.get("families", {}).items() }

        # canonical -> category
        self.cats: dict[str, str] = {}
        # category -> set(canonical)
        self.by_cat: dict[str, set[str]] = defaultdict(set)
        # all canonical skills
        self.all_canon: set[str] = set()
        # all surface forms (canonical + aliases) لأغراض الـ embeddings
        self.surface, self.to_canon = [], []

        for it in skills:
            can = it["canonical"].strip()
            cat = it.get("category", "other")
            self.cats[can] = cat
            self.by_cat[cat].add(can)
            self.all_canon.add(can)

            forms = [can] + [a.strip() for a in it.get("aliases", []) if a.strip()]
            for s in forms:
                s_norm = _tok(s)
                if not s_norm:
                    continue
                self.surface.append(s_norm)
                self.to_canon.append(can)

        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.emb_surface = self.model.encode(self.surface, convert_to_tensor=True)

    def category(self, canonical: str) -> str:
        return self.cats.get(canonical, "other")

    def categories(self, canon_set):
        return {self.cats.get(c, "other") for c in (canon_set or set())}

    def normalize_list(self, skills_list):
        skills_list = [s.strip() for s in (skills_list or []) if s.strip()]
        if not skills_list:
            return set()

        q_norm = [_tok(s) for s in skills_list if _tok(s)]
        if not q_norm:
            return set()

        q_emb = self.model.encode(q_norm, convert_to_tensor=True)   # (U, d)
        sims = util.cos_sim(q_emb, self.emb_surface)                # (U, M)
        maxv, argmax = sims.max(dim=1)
        out = set()
        for v, j in zip(maxv.tolist(), argmax.tolist()):
            if v >= self.threshold:
                out.add(self.to_canon[j])
        return out

    def _ngrams(self, text, max_n=4):
        toks = _tok(text).split()
        out = set()
        for n in range(1, max_n+1):
            for i in range(len(toks)-n+1):
                out.add(" ".join(toks[i:i+n]))
        return list(out)

    def normalize_text(self, text):
        """تحويل نص الـJD إلى مجموعة مهارات canonical + توسيع من families."""
        out = set()

        # (1) تشابه دلالي على n-grams
        cands = self._ngrams(text, max_n=4)
        if cands:
            q_emb = self.model.encode(cands, convert_to_tensor=True)  # (C, d)
            sims = util.cos_sim(q_emb, self.emb_surface)              # (C, M)
            maxv, argmax = sims.max(dim=1)
            for v, j in zip(maxv.tolist(), argmax.tolist()):
                if v >= self.threshold:
                    out.add(self.to_canon[j])

        # (2) توسعة كلمات/عائلات من JSON
        text_low = _tok(text)
        for key, family in self.family_keywords.items():
            if key and key in text_low:
                out.update(family)

        return out

    # ---------- جديد: اقتراح مهارات عامة من نفس فئات الـJD ----------
    def suggest_by_categories(self, categories, exclude=None, per_cat=2, total=10):
        """
        اقترح مهارات من نفس الفئات (categories) الموجودة في الـontology،
        باستثناء أي مهارات موجودة في exclude.
        - categories: مجموعة فئات مستهدفة (مثل {"frontend","backend",...})
        - exclude: set لمهارات canonical لاستثنائها (مثل user_can | jd_can)
        - per_cat: حد أقصى لعدد المقترحات لكل فئة
        - total: حد أقصى إجمالي
        """
        exclude = exclude or set()
        out = []
        # ترتيب حتمي للاستقرار
        for cat in sorted(list(categories)):
            count_cat = 0
            pool = sorted(list(self.by_cat.get(cat, set())))
            for can in pool:
                if can in exclude:
                    continue
                out.append(can)
                count_cat += 1
                if per_cat and count_cat >= per_cat:
                    break
                if total and len(out) >= total:
                    return out[:total]
        return out[:total]
