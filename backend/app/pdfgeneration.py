# app/pdfgeneration.py
import os, io, re
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

    SUBTITLE_INDENT = 16     # إزاحة يسار للـ subtitle والسطور التابعة له
    SUBTITLE_AFTER_GAP = 4   # فراغ صغير بعد كل بلوك subtitle


    TITLE_SZ = 16
    SUB_SZ   = 12
    BODY_SZ  = 12
    SMALL_SZ = 11

    LINE              = 17
    LINE_SIDE         = 14
    BULLET_INDENT     = 12
    SECTION_GAP       = 28
    SIDE_SECTION_GAP  = 12
    AFTER_PARA_GAP    = 10
    AFTER_BULLETS_GAP = 16

    # ---------- HELPERS ----------
    def text_width(text, font="Helvetica", size=BODY_SZ):
        return pdfmetrics.stringWidth(text, font, size)

    def wrap_text(text, font="Helvetica", size=BODY_SZ, max_width=300):
        """
        لف النص على عرض محدد باستخدام قياسات الخط.
        """
        words = (text or "").split()
        lines, line = [], ""
        for w in words:
            test = (line + " " + w).strip()
            if pdfmetrics.stringWidth(test, font, size) <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        if not lines:
            lines = [""]
        return lines

    def draw_divider(x1, y, x2):
        p.setStrokeColor(line_color)
        p.setLineWidth(0.7)
        p.line(x1, y, x2, y)

    # Bulleted list (يمين)
    def draw_bullets(items, start_y, max_w, bullet="•", font="Helvetica", size=BODY_SZ,
                     indent=BULLET_INDENT, line=LINE, after_gap=4, start_x=0):
        y = start_y
        for item in (items or []):
            item = (item or "").strip()
            if not item:
                continue
            btxt = f"{bullet} "
            bw = text_width(btxt, font, size)
            avail = max_w - indent - bw
            lines = wrap_text(item, font=font, size=size, max_width=avail)

            # أول سطر مع الرمز
            if y < 80:
                p.showPage(); draw_sidebar_bg()
                y = H - 90
            p.setFont(font, size)
            p.drawString(start_x + indent, y, btxt)
            p.drawString(start_x + indent + bw, y, lines[0])
            y -= line

            # بقية السطور بدون رمز
            for ln in lines[1:]:
                if y < 80:
                    p.showPage(); draw_sidebar_bg()
                    y = H - 90
                p.drawString(start_x + indent + bw, y, ln)
                y -= line
            y -= after_gap
        return y

    # رسم نص ملتف على إحداثيات محددة
    def draw_wrapped_at(x, y, text, max_w, font="Helvetica", size=BODY_SZ, leading=LINE):
        p.setFont(font, size)
        for ln in wrap_text(text, font=font, size=size, max_width=max_w):
            if y < 80:
                p.showPage(); draw_sidebar_bg()
                y = H - 90
            p.drawString(x, y, ln)
            y -= leading
        return y

    # ---------- LAYOUT ----------
    margin = 40
    left_w = 190
    right_x = margin + left_w + 24
    right_w = W - right_x - margin

    def draw_sidebar_bg():
        p.setFillColor(dark)
        p.rect(margin, margin, left_w, H - 2*margin, stroke=0, fill=1)

    draw_sidebar_bg()

    # ---------- LLM POLISH (optional) ----------
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

    # === derive role/specialization tag - NO hardcoded titles, NO "Software Engineer" fallback ===
    def _clean_text(s: str) -> str:
        s = s.strip(" -—|()")
        if s and (s.isupper() or s.islower()):
            return s.title()
        return s

    def derive_tag():
        edu = (payload.education or "").strip()

        # 1) حاول أولاً استخراج الاختصاص من التعليم (يغلب على أي شيء آخر)
        if edu:
            import re
            # يدعم الإنكليزي والعربي: in / of / في
            m = re.search(r'(?:\b(?:in|of)\b|في)\s+([^—\-\(\)|]{2,80})', edu, flags=re.IGNORECASE)
            if m:
                field = _clean_text(m.group(1))
                if 2 <= len(field) <= 80:
                    return field

            # بديل: جزّئ على الفواصل الشائعة وخُذ أطول جزء يبدو أنه اختصاص (استبعد سنوات وألقاب الدرجة)
            parts = [p.strip() for p in re.split(r'[—\-|]', edu) if p.strip()]
            if parts:
                DEGREE_HINTS = ("b.sc", "m.sc", "ph.d", "bachelor", "master", "degree", "diploma", "associate", "bootcamp",
                                "بكالوريوس", "ماجستير", "دكتوراه", "شهادة")
                def looks_like_field(txt: str) -> bool:
                    low = txt.lower()
                    if any(h in low for h in DEGREE_HINTS):
                        return False
                    if re.search(r'\b\d{4}\b', low):
                        return False
                    return True
                candidates = [p for p in parts if looks_like_field(p)]
                if candidates:
                    field = _clean_text(max(candidates, key=len))
                    if field:
                        return field

        # 2) إذا التعليم ما عطى نتيجة: جرّب Title من LLM، لكن تجاهل العناوين العامة جداً
        if polished and isinstance(polished.get("title"), str):
            t = polished["title"].strip()
            if t and t.lower() not in {"software engineer", "candidate"}:
                return t

        # 3) كحلّ أخير: أول مهارة كما هي (حتى 3 كلمات)، بدون تحويلها لألقاب جاهزة
        skills_text = (payload.skills or "").strip()
        if skills_text:
            first_skill = skills_text.split(",")[0].strip()
            if first_skill:
                words = first_skill.split()
                field = _clean_text(" ".join(words[:3]))
                if field:
                    return field

        # 4) fallback الأخير
        return "Candidate"

    tag = derive_tag()
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

    # SKILLS
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
    yL -= SIDE_SECTION_GAP

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
        for row in wrap_text(ln, font="Helvetica", size=SMALL_SZ, max_width=maxw):
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
        y = draw_wrapped_at(right_x, y, text or "—", right_w, font="Helvetica", size=BODY_SZ, leading=LINE)
        y -= AFTER_PARA_GAP

    # PROFILE
    right_section("Profile")
    if polished and polished.get("professional_summary"):
        profile_text = polished["professional_summary"]
    else:
        profile_src = (payload.experience or "").strip() or (payload.education or "").strip()
        profile_text = " ".join(profile_src.split())[:600] if profile_src else "—"
    draw_paragraph(profile_text)
    y -= SECTION_GAP

    # --------- WORK EXPERIENCE (Subtitle + Bullets + Blocks) ----------
    right_section("Work Experience")

    subtitle_re = re.compile(r"^\s*([^:\n]{2,80})\s*:\s*(.*)$")

    def draw_experience_block(block_text, leading=LINE):
        nonlocal y
        lines = [ln.rstrip() for ln in block_text.splitlines()]
        for ln in lines:
            if not ln.strip():
                y -= leading * 0.6
                continue

            # Bullet
            if ln.lstrip().startswith("-"):
                bullet_text = ln.lstrip()[1:].strip()
                y = draw_bullets(
                    [bullet_text], start_y=y, max_w=right_w,
                    bullet="•", font="Helvetica", size=BODY_SZ,
                    indent=BULLET_INDENT, line=LINE, after_gap=2, start_x=right_x
                )
                continue

            # Subtitle: "Title: details"
            m = subtitle_re.match(ln)
            if m:
                title, details = m.group(1).strip(), m.group(2).strip()

                # نقطة البداية المزاحة لليسار
                sx = right_x + SUBTITLE_INDENT

                # قياسات الخطوط
                p_font_bold = "Helvetica-Bold"
                p_font_reg  = "Helvetica"
                p_size      = SUB_SZ

                title_txt = title + ": "
                title_w = text_width(title_txt, p_font_bold, p_size)

                # العرض المُتاح بعد الإزاحة
                avail_full = right_w - SUBTITLE_INDENT

                # إذا العنوان بيسع مع التفاصيل على نفس السطر
                if title_w < avail_full * 0.9:
                    if y < 80:
                        p.showPage(); draw_sidebar_bg()
                        y = H - 90

                    # ارسم العنوان الغامق مع إزاحة
                    p.setFont(p_font_bold, p_size)
                    p.drawString(sx, y, title_txt)

                    # ارسم التفاصيل بجانبه مع لف، والبداية أيضاً بإزاحة
                    p.setFont(p_font_reg, p_size)
                    avail_details = avail_full - title_w
                    lines_det = wrap_text(details, font=p_font_reg, size=p_size, max_width=avail_details)

                    if lines_det:
                        # أول سطر على نفس السطر
                        p.drawString(sx + title_w, y, lines_det[0])
                        y -= LINE
                        # السطور التالية تبدأ من sx (نفس الإزاحة)
                        for extra in lines_det[1:]:
                            if y < 80:
                                p.showPage(); draw_sidebar_bg()
                                y = H - 90
                            p.drawString(sx, y, extra)
                            y -= LINE
                    else:
                        y -= LINE
                else:
                    # العنوان كبير → سطر لحاله بإزاحة، ثم التفاصيل تحته بإزاحة
                    y = draw_wrapped_at(sx, y, title + ":", avail_full,
                                        font=p_font_bold, size=p_size, leading=LINE)
                    if details:
                        y = draw_wrapped_at(sx, y, details, avail_full,
                                            font=p_font_reg, size=p_size, leading=LINE)

                # فراغ بسيط بعد كل subtitle block
                y -= SUBTITLE_AFTER_GAP
                continue


            # سطر عادي
            y = draw_wrapped_at(right_x, y, ln, right_w, font="Helvetica", size=BODY_SZ, leading=LINE)

        # مسافة إضافية بعد كل بلوك
        y -= 6

    # تقسيم الخبرة إلى Blocks بسطر فاضي
    raw_exp = (payload.experience or "").strip()
    blocks = [b.strip() for b in re.split(r"\n\s*\n", raw_exp) if b.strip()]

    if polished and polished.get("experience_bullets") and not blocks:
        # fallback (لو ما في فورمات)
        bullets = polished["experience_bullets"]
        y = draw_bullets(bullets, start_y=y, max_w=right_w, start_x=right_x,
                         bullet="•", size=BODY_SZ, indent=BULLET_INDENT, line=LINE, after_gap=4)
    else:
        for i, block in enumerate(blocks):
            draw_experience_block(block)
            if i < len(blocks) - 1:
                y -= AFTER_BULLETS_GAP
    y -= SECTION_GAP

    # EDUCATION
    right_section("Education")
    if polished and polished.get("education_section"):
        edu_bullets = polished["education_section"][:6]
        y = draw_bullets(edu_bullets, start_y=y, max_w=right_w, start_x=right_x,
                         bullet="•", size=BODY_SZ, indent=BULLET_INDENT, line=LINE, after_gap=2)
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
