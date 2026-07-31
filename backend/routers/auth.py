"""認證相關 API 路由（登入/登出/註冊）"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..common import hash_password, verify_password
from ..database import get_db

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=schemas.Member, status_code=201)
def register(data: schemas.MemberRegister, db: Session = Depends(get_db)):
    """註冊新會員：驗證 Email 唯一性，建立會員資料"""
    email = data.email.lower().strip()
    # 檢查 Email 是否已被註冊
    if db.query(models.Member).filter_by(email=email).first():
        raise HTTPException(409, "此 Email 已經註冊")
    # 建立新會員（密碼經雜湊處理）
    member = models.Member(email=email, password_hash=hash_password(data.password),
        display_name=data.display_name.strip(), gender=data.gender, zodiac=data.zodiac,
        city=data.city.strip(), interests=data.interests.strip())
    db.add(member); db.commit(); db.refresh(member)
    return member


@router.post("/login", response_model=schemas.LoginResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """登入：驗證帳號密碼，成功則回傳會員編號與顯示名稱"""
    member = db.query(models.Member).filter_by(email=data.email.lower().strip()).first()
    if not member or not verify_password(data.password, member.password_hash):
        raise HTTPException(401, "Email 或密碼錯誤")
    return {"member_id": member.id, "display_name": member.display_name}


@router.post("/logout")
def logout():
    """登出（前端負責清除 sessionStorage）"""
    return {"message": "已登出"}
