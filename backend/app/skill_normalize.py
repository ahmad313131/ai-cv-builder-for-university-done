# app/skill_normalize.py
import json, re
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

        # دعم خلفي: إذا الملف القديم كان list مباشرة
        skills = data.get("skills", data if isinstance(data, list) else [])
        self.family_keywords = { (k or "").lower(): set(v) for k, v in data.get("families", {}).items() }

        # canonical -> category
        self.cats = {}
        # all surface forms (canonical + aliases)
        self.surface, self.to_canon = [], []

        for it in skills:
            can = it["canonical"].strip()
            self.cats[can] = it.get("category", "other")
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
