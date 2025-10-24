# app/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os

# --- DB bootstrap ---
from .database import Base, engine
from .models import User, CV  # ensure models are registered
Base.metadata.create_all(bind=engine)

# --- Routers ---
from .auth import router as auth_router
from .routers.cvs import router as cvs_router
from .pdfgeneration import router as pdf_router
from .ai_analysis import router as ai_router
from .ai_llm import router as llm_router

app = FastAPI(title="AI CV Builder API", version="0.4")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # أضف هنا دومين النشر لاحقًا مثل:
        # "https://your-frontend.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static uploads ---
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- Include routers ---
app.include_router(auth_router)
app.include_router(cvs_router)
app.include_router(pdf_router)
app.include_router(ai_router)
app.include_router(llm_router)

# --- Health/status ---
@app.get("/api/status")
def status():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

# --- Upload photo (used by frontend) ---
@app.post("/api/upload_photo")
async def upload_photo(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Only .png, .jpg, .jpeg are supported")

    fname = f"{int(datetime.utcnow().timestamp())}_{file.filename}"
    save_path = os.path.join("uploads", fname)

    # احفظ الملف
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # مسار يمكن استعماله مباشرة من الواجهة ومن توليد الـ PDF
    return {"path": f"/uploads/{fname}"}
