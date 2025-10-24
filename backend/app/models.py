# app/models.py
# قبل (ينقصه ForeignKey):
# from sqlalchemy import Column, Integer, String, DateTime, Text, func

# بعد (الصحيح):
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cvs = relationship("CV", back_populates="owner", cascade="all, delete-orphan")

class CV(Base):
    __tablename__ = "cvs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(120))
    education = Column(Text)
    experience = Column(Text)
    skills = Column(Text)
    github = Column(String(255))
    linkedin = Column(String(255))
    languages = Column(Text)
    hobbies = Column(Text)
    photo_path = Column(String(255))
    job_description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # الربط بالمستخدم
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    owner = relationship("User", back_populates="cvs")
