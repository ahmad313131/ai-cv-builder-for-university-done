# app/schemas.py
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
