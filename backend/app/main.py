from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
from reportlab.lib.utils import ImageReader

from datetime import datetime
import json
import os
import io

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# NLP & Dataset
import pandas as pd
from sentence_transformers import SentenceTransformer, util


# ---------- Models ----------

from typing import Optional
from pydantic import BaseModel, EmailStr

class CVIn(BaseModel):
    name: str
    email: EmailStr
    education: str = ""
    experience: str = ""
    skills: str = ""
    github: str = ""
    linkedin: str = ""
    languages: str = ""   # NEW: "English: Proficient, Arabic: Native"
    hobbies: str = ""     # NEW: "Reading, Football"
    photo_path: str = ""  # NEW: مثل "/uploads/16999_photo.jpg"
    job_description: Optional[str] = ""  


class CVOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: str
    note: str = ""


# ---------- App setup ----------
app = FastAPI(title="AI CV Builder API", version="0.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

DATA_FILE = "cv_db.json"

from .pdfgeneration import router as pdf_router
from .ai_analysis import router as ai_router
from .ai_llm import router as llm_router
from .schemas import CVIn, CVOut
app.include_router(llm_router)
app.include_router(pdf_router)
app.include_router(ai_router)
# ---------- DB helpers ----------
def load_db():
    if not os.path.exists(DATA_FILE):
        return {"next_id": 1, "items": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


# ---------- Endpoints ----------
@app.get("/api/status")
def status():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}


@app.post("/api/cv", response_model=CVOut)
def receive_cv(payload: CVIn):
    db = load_db()
    item = {
    "id": db["next_id"],
    "name": payload.name,
    "email": payload.email,
    "education": payload.education,
    "experience": payload.experience,
    "skills": payload.skills,
    "github": payload.github,
    "linkedin": payload.linkedin,
    "languages": payload.languages,   # NEW
    "hobbies": payload.hobbies,       # NEW
    "photo_path": payload.photo_path, # NEW
    "created_at": datetime.utcnow().isoformat() + "Z",
    "analysis": {"matching_score": None, "suggestions": []}
}

    db["items"].append(item)
    db["next_id"] += 1
    save_db(db)

    return CVOut(id=item["id"], name=item["name"], email=item["email"],
                 created_at=item["created_at"],
                 note="Received. Analysis placeholders available in DB.")


@app.get("/api/cv/{cv_id}")
def get_cv(cv_id: int):
    db = load_db()
    for it in db["items"]:
        if it["id"] == cv_id:
            return it
    raise HTTPException(status_code=404, detail="CV not found")


@app.get("/api/cvs")
def list_cvs():
    db = load_db()
    return {"total": len(db["items"]), "items": db["items"]}

#----------------upload photo---------------#
@app.post("/api/upload_photo")
async def upload_photo(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Only .png, .jpg, .jpeg are supported")

    fname = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
    save_path = os.path.join("uploads", fname)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # بيرجع مسار تقدر تستخدمه مباشرة بالرّياكت وبالـPDF
    return {"path": f"/uploads/{fname}"}


# ---------- PDF GENERATION ----------
# ---------- NLP Analysis with Dataset ----------
