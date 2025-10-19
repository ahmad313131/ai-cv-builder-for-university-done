# app/pdfgeneration.py
import os, io
from datetime import datetime
from fastapi import APIRouter, Response
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader

from .schemas import CVIn  # استيراد من schemas لتفادي circular
from .ai_llm import polish_cv_struct  # LLM polisher (ديناميكي)

router = APIRouter()

@router.post("/api/generate_cv")
def generate_cv(payload: CVIn):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4

    # ---------- THEME / SCALES ----------
    dark = colors.HexColor("#202833")
    light_text = colors.HexColor("#C9D3DF")
    line_color = colors.HexColor("#D7DEE7")
    body_text = colors.HexColor("#2B2B2B")

    # Typography & rhythm
    TITLE_SZ = 14
    SUB_SZ = 11
    BODY_SZ = 11
    SMALL_SZ = 10

    LINE = 15             # line-height main column
    LINE_SIDE = 13        # line-height sidebar
    BULLET_INDENT = 10    # px indent from left edge of right column
    SECTION_GAP = 14      # gap after sections in right column
    SIDE_SECTION_GAP = 10 # gap after sections in sidebar

    # ---------- HELPERS ----------
    def text_width(text, font="Helvetica", size=BODY_SZ):
        return pdfmetrics.stringWidth(text, font, size)

    def wrap_text(text, max_w, font="Helvetica", size=BODY_SZ):
        words = (text or "").split()
        lines, cur = [], ""
        for w in words or [""]:
            test = (cur + " " + w).strip()
            if text_width(test, font, size) <= max_w:
                cur = test
            else:
                if cur: lines.append(cur)
                cur = w
        if cur: lines.append(cur)
        return lines or ["—"]

    def draw_divider(x1, y, x2):
        p.setStrokeColor(line_color)
        p.setLineWidth(0.7)
        p.line(x1, y, x2, y)

    # Bulleted list for the right column (with indent & wrapping)
    def draw_bullets(items, max_w, start_y, bullet="•", font="Helvetica", size=BODY_SZ, indent=BULLET_INDENT, line=LINE, after_gap=4):
        y = start_y
        for item in (items or []):
            item = (item or "").strip()
            if not item:
                continue
            # bullet + space width
            btxt = f"{bullet} "
            bw = text_width(btxt, font, size)
            # available line width after bullet
            avail = max_w - indent - bw
            # wrap content
            lines = wrap_text(item, avail, font, size)
            # draw first line with bullet
            if y < 80:  # new page safety
                p.showPage(); draw_sidebar_bg()
                y = H - 90
            p.setFont(font, size)
            p.drawString(right_x + indent, y, btxt)
            p.drawString(right_x + indent + bw, y, lines[0])
            y -= line
            # subsequent lines aligned with content (no bullet)
            for ln in lines[1:]:
                if y < 80:
                    p.showPage(); draw_sidebar_bg()
                    y = H - 90
                p.drawString(right_x + indent + bw, y, ln)
                y -= line
            y -= after_gap
        return y

    # ---------- LAYOUT ----------
    margin = 36
    left_w = 190
    right_x = margin + left_w + 24
    right_w = W - right_x - margin

    def draw_sidebar_bg():
        p.setFillColor(dark)
        p.rect(margin, margin, left_w, H - 2*margin, stroke=0, fill=1)

    draw_sidebar_bg()

    # ---------- LLM POLISH (optional, fallback-safe) ----------
    use_llm = os.getenv("USE_LLM_POLISH", "1") == "1"
    polished = None
    if use_llm:
        try:
            polished = polish_cv_struct(payload)
        except Exception:
            polished = None  # لا نوقف التوليد إذا LLM وقع

    # ---------- PHOTO ----------
    cx, cy, r = margin + left_w/2, H - 120, 44
    photo_drawn = False

    if payload.photo_path:
        local = payload.photo_path.strip()
        if local.startswith(("http://", "https://")):
            local = local.replace("http://127.0.0.1:8000", "").replace("http://localhost:8000", "")
        local_fs = local.lstrip("/").replace("/", os.sep)
        abs_path = os.path.abspath(local_fs)
        try:
            p.saveState()
            path = p.beginPath()
            path.circle(cx, cy, r)
            p.clipPath(path, stroke=0)
            img = ImageReader(abs_path)
            p.drawImage(img, cx - r, cy - r, 2*r, 2*r, mask='auto')
            p.restoreState()
            photo_drawn = True
        except Exception as e:
            print("PDF photo error:", e, "| tried path:", abs_path)

    if not photo_drawn:
        p.setFillColor(colors.HexColor("#2E3A49"))
        p.circle(cx, cy, r, stroke=0, fill=1)
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 20)
        initials = "".join([part[:1] for part in (payload.name or '').split()][:2]).upper() or "CV"
        p.drawCentredString(cx, cy-7, initials)

    # ---------- NAME & TAG ----------
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 14)
    display_name = (polished.get("name") if polished else payload.name) or "Your Name"
    p.drawCentredString(cx, cy - 70, display_name)

    tag = (polished.get("title") if polished else None)
    if not tag:
        tag = "Software Engineer" if any(k in (payload.skills or "").lower()
              for k in ["python","js","react","java","ml","ai"]) else "Candidate"
    p.setFont("Helvetica", SMALL_SZ)
    p.setFillColor(light_text)
    p.drawCentredString(cx, cy - 86, tag)

    # ---------- SIDEBAR SECTIONS ----------
    def left_title(y, title):
        p.setFillColor(light_text)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(margin + 16, y, title)
        p.setFillColor(colors.white)
        p.setLineWidth(0.8)
        p.line(margin + 16, y-4, margin + left_w - 16, y-4)
        return y - 14

    yL = cy - 120

    # SKILLS (dynamic buckets → flat)
    yL = left_title(yL, "SKILLS")

    def merged_skills():
        if polished:
            flat = polished.get("key_skills_flat")
            if isinstance(flat, list) and flat:
                return flat[:30]
            ks = polished.get("key_skills") or {}
            if isinstance(ks, dict) and ks:
                out = []; seen = set()
                for arr in ks.values():
                    for s in (arr or []):
                        if s and s not in seen:
                            seen.add(s); out.append(s)
                return out[:30]
        return [s.strip() for s in (payload.skills or "").split(",") if s.strip()][:30]

    p.setFont("Helvetica", SMALL_SZ)
    for s in (merged_skills() or ["—"]):
        p.drawString(margin + 16, yL, f"• {s}")
        yL -= LINE_SIDE
        if yL < 90: break
    yL -= SIDE_SECTION_GAP  # extra gap after skills

    # CONTACT
    yL = left_title(yL, "CONTACT")
    p.setFont("Helvetica", SMALL_SZ)
    p.setFillColor(colors.white)

    links = (polished.get("links") if polished else {}) or {}
    email = links.get("email") or payload.email
    linkedin = links.get("linkedin") or (payload.linkedin or "")
    github = links.get("github") or (payload.github or "")

    contact = [f"Email: {email}"]
    if linkedin: contact.append(f"LinkedIn: {linkedin}")
    if github:   contact.append(f"GitHub: {github}")

    maxw = left_w - 32
    for ln in contact:
        for row in wrap_text(ln, maxw, "Helvetica", SMALL_SZ):
            p.drawString(margin + 16, yL, row)
            yL -= LINE_SIDE
    yL -= SIDE_SECTION_GAP


    # LANGUAGES
    yL = left_title(yL, "LANGUAGES")
    p.setFont("Helvetica", SMALL_SZ)
    if polished and polished.get("languages"):
        langs = polished["languages"]
    else:
        langs = [s.strip() for s in (payload.languages or "").split(",") if s.strip()]
    for s in (langs or ["—"]):
        p.drawString(margin + 16, yL, f"• {s}")
        yL -= LINE_SIDE
        if yL < 75: break
    yL -= SIDE_SECTION_GAP

    # HOBBIES
    yL = left_title(yL, "HOBBIES")
    p.setFont("Helvetica", SMALL_SZ)
    if polished and polished.get("hobbies"):
        hobs = polished["hobbies"]
    else:
        hobs = [s.strip() for s in (payload.hobbies or "").split(",") if s.strip()]
    for s in (hobs or ["—"]):
        p.drawString(margin + 16, yL, f"• {s}")
        yL -= LINE_SIDE
        if yL < 60: break
    # (لا نحتاج gap أخير بالشريط الجانبي)

    # ---------- RIGHT CONTENT ----------
    y = H - 72
    def right_section(title):
        nonlocal y
        if y < 110:
            p.showPage(); draw_sidebar_bg()
            y = H - 72
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", TITLE_SZ)
        p.drawString(right_x, y, title.upper())
        y -= 8
        draw_divider(right_x, y, W - margin)
        y -= 14
        p.setFont("Helvetica", BODY_SZ)
        p.setFillColor(body_text)

    def draw_paragraph(text):
        nonlocal y
        for ln in wrap_text(text or "—", right_w, "Helvetica", BODY_SZ):
            if y < 80:
                p.showPage(); draw_sidebar_bg()
                y = H - 90
            p.drawString(right_x, y, ln)
            y -= LINE
        y -= 6  # small gap after paragraph

    # PROFILE → professional_summary أولاً
    right_section("Profile")
    if polished and polished.get("professional_summary"):
        profile_text = polished["professional_summary"]
    else:
        profile_src = (payload.experience or "").strip() or (payload.education or "").strip()
        profile_text = " ".join(profile_src.split())[:600] if profile_src else "—"
    draw_paragraph(profile_text)
    y -= SECTION_GAP  # extra spacing after section

    # WORK EXPERIENCE → polished bullets إن وُجدت
    right_section("Work Experience")
    if polished and polished.get("experience_bullets"):
        bullets = polished["experience_bullets"]
    else:
        raw_exp = payload.experience or ""
        bullets = [b.strip("•- ").strip() for b in (raw_exp.replace("•","\n").replace("- ","\n").splitlines()) if b.strip()]
    y = draw_bullets(bullets[:12], right_w, y, bullet="•", size=BODY_SZ, indent=BULLET_INDENT, line=LINE, after_gap=4)
    y -= SECTION_GAP

    # EDUCATION
    right_section("Education")
    if polished and polished.get("education_section"):
        edu_bullets = polished["education_section"][:6]
        y = draw_bullets(edu_bullets, right_w, y, bullet="•", size=BODY_SZ, indent=BULLET_INDENT, line=LINE, after_gap=2)
    else:
        draw_paragraph(payload.education)

    # FOOTER
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(colors.HexColor("#888888"))
    p.drawRightString(W - margin, margin - 6 + 20, f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

    p.showPage()
    p.save()
    buffer.seek(0)

    fname = (polished.get("name") if polished else payload.name) or "CV"
    safe = "".join(c for c in fname if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    return Response(
        buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={safe}_CV.pdf"}
    )
