# app/routers/cvs.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CV
from ..auth import get_current_user
from ..schemas import CVIn, CVOut, CVDetail

router = APIRouter(prefix="/api", tags=["cvs"])

@router.post("/cv", response_model=CVOut)
def create_cv(payload: CVIn, db: Session = Depends(get_db), current=Depends(get_current_user)):
    cv = CV(
        name=payload.name,
        email=payload.email,
        education=payload.education,
        experience=payload.experience,
        skills=payload.skills,
        github=payload.github,
        linkedin=payload.linkedin,
        languages=payload.languages,
        hobbies=payload.hobbies,
        photo_path=payload.photo_path,
        job_description=payload.job_description,
        user_id=current.id,  # ✅ ربط بالمستخدم
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return CVOut(
        id=cv.id,
        name=cv.name,
        email=cv.email,
        created_at=str(cv.created_at) if cv.created_at else "",
        note="Stored in database ✅",
    )

@router.get("/cv/{cv_id}", response_model=CVOut)
def get_cv(cv_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    cv = db.query(CV).filter(CV.id == cv_id, CV.user_id == current.id).first()
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV not found")
    return CVOut(
        id=cv.id,
        name=cv.name,
        email=cv.email,
        created_at=str(cv.created_at) if cv.created_at else "",
        note=""
    )

# ✅ جديد: رجّع كل الحقول المخزّنة للسجل (لاستخدامها بالـ PDF)
@router.get("/cv/{cv_id}/raw", response_model=CVDetail)
def get_cv_raw(cv_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    cv = db.query(CV).filter(CV.id == cv_id, CV.user_id == current.id).first()
    if not cv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV not found")

    return CVDetail(
        id=cv.id,
        name=cv.name,
        email=cv.email,
        education=cv.education or "",
        experience=cv.experience or "",
        skills=cv.skills or "",
        github=cv.github or "",
        linkedin=cv.linkedin or "",
        languages=cv.languages or "",
        hobbies=cv.hobbies or "",
        photo_path=cv.photo_path or "",
        job_description=cv.job_description or "",
        created_at=cv.created_at.isoformat() if cv.created_at else "",
    )

@router.get("/cvs", response_model=list[CVOut])
def list_cvs(db: Session = Depends(get_db), current=Depends(get_current_user)):
    items = db.query(CV).filter(CV.user_id == current.id).order_by(CV.id.desc()).all()
    return [
        CVOut(
            id=it.id,
            name=it.name,
            email=it.email,
            created_at=str(it.created_at) if it.created_at else "",
            note=""
        )
        for it in items
    ]
