from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..common import hash_password, verify_password
from ..database import get_db

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=schemas.Member, status_code=201)
def register(data: schemas.MemberRegister, db: Session = Depends(get_db)):
    email = data.email.lower().strip()
    if db.query(models.Member).filter_by(email=email).first():
        raise HTTPException(409, "此 Email 已經註冊")
    member = models.Member(email=email, password_hash=hash_password(data.password),
        display_name=data.display_name.strip(), city=data.city.strip(),
        interests=data.interests.strip())
    db.add(member); db.commit(); db.refresh(member)
    return member


@router.post("/login", response_model=schemas.LoginResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    member = db.query(models.Member).filter_by(email=data.email.lower().strip()).first()
    if not member or not verify_password(data.password, member.password_hash):
        raise HTTPException(401, "Email 或密碼錯誤")
    return {"member_id": member.id, "display_name": member.display_name}


@router.post("/logout")
def logout():
    return {"message": "已登出"}
