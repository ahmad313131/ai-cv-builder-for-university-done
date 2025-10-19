# app/utils_actions.py
import json, re, hashlib
from pathlib import Path
from typing import Dict, List, Tuple

_CONFIG_CACHE: Tuple[Dict, float] | None = None

def load_action_config() -> Dict:
    """Load app/data/action_verbs.json (cached)."""
    global _CONFIG_CACHE
    base = Path(__file__).resolve().parent
    path = (base / "data" / "action_verbs.json")
    mtime = path.stat().st_mtime
    if _CONFIG_CACHE and _CONFIG_CACHE[1] == mtime:
        return _CONFIG_CACHE[0]
    with path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    _CONFIG_CACHE = (cfg, mtime)
    return cfg

def infer_domains(skill_text: str, cfg: Dict) -> List[str]:
    skill_text = (skill_text or "").lower()
    doms = []
    domains = cfg.get("domains", {})
    for name, obj in domains.items():
        kws = [k.lower() for k in obj.get("keywords", [])]
        if any(k in skill_text for k in kws):
            doms.append(name)
    return doms

def build_verb_pool(domains: List[str], cfg: Dict) -> List[str]:
    pool = []
    seen = set()
    domains = domains or []
    dom_cfg = cfg.get("domains", {})
    for d in domains:
        for v in dom_cfg.get(d, {}).get("verbs", []):
            if v not in seen:
                seen.add(v); pool.append(v)
    for v in cfg.get("default_verbs", []):
        if v not in seen:
            seen.add(v); pool.append(v)
    return pool or cfg.get("default_verbs", ["Developed","Implemented","Built"])

def starts_with_verb(line: str, cfg: Dict) -> bool:
    if not line: return False
    first = re.split(r"\s+", line.strip())[0].lower().strip("•-:")
    any_verbs = set(v.lower() for v in cfg.get("default_verbs", []))
    for d in cfg.get("domains", {}).values():
        any_verbs.update(v.lower() for v in d.get("verbs", []))
    return first in any_verbs

def pick_verb_deterministic(text: str, verb_pool: List[str]) -> str:
    if not verb_pool:
        return "Developed"
    h = hashlib.md5((text or "").strip().encode("utf-8")).hexdigest()
    idx = int(h[:8], 16) % len(verb_pool)
    return verb_pool[idx]
