# app/schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

# ========= CV =========

class CVIn(BaseModel):
    name: str
    email: EmailStr
    education: str = ""
    experience: str = ""
    skills: str = ""
    github: str = ""
    linkedin: str = ""
    languages: str = ""   # e.g., "English: Proficient, Arabic: Native"
    hobbies: str = ""     # e.g., "Reading, Football"
    photo_path: str = ""  # e.g., "/uploads/16999_photo.jpg"
    job_description: Optional[str] = ""

class CVOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: str
    note: str = ""

class CVDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # ✅ v2 style

    id: int
    name: str
    email: EmailStr
    education: str = ""
    experience: str = ""
    skills: str = ""
    github: str = ""
    linkedin: str = ""
    languages: str = ""
    hobbies: str = ""
    photo_path: str = ""
    job_description: Optional[str] = ""
    created_at: str = ""   # نرجّعها كنص (isoformat)

# ========= Users / Auth =========

class UserCreate(BaseModel):
    email: EmailStr
    password: str  # (اختياري) ممكن تضيف قواعد طول/تعقيد بالباكند
    username: str  

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # ✅ v2 style
    id: int
    email: EmailStr
    username: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
