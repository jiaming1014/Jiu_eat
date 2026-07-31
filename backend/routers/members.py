"""會員資料相關 API 路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..common import activity_json, application_json, member_or_404
from ..database import get_db

router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("/{member_id}", response_model=schemas.Member)
def get_member(member_id: int, db: Session = Depends(get_db)):
    """取得單一會員的完整資料"""
    return member_or_404(db, member_id)


@router.put("/{member_id}", response_model=schemas.Member)
def update_member(member_id: int, data: schemas.MemberUpdate, db: Session = Depends(get_db)):
    """更新會員個人資料（逐欄位更新，字串自動去除空白）"""
    member = member_or_404(db, member_id)
    for key, value in data.model_dump().items():
        setattr(member, key, value.strip() if isinstance(value, str) else value)
    db.commit(); db.refresh(member)
    return member


@router.get("/{member_id}/activities")
def member_activities(member_id: int, db: Session = Depends(get_db)):
    """取得會員建立的活動與提出的申請列表"""
    member_or_404(db, member_id)
    # 查詢該會員建立的活動（依活動時間排序）
    created = db.query(models.Activity).filter_by(organizer_id=member_id).order_by(models.Activity.activity_date).all()
    # 查詢該會員提出的申請（依申請時間倒序）
    applications = db.query(models.Application).filter_by(member_id=member_id).order_by(models.Application.created_at.desc()).all()
    return {"created": [activity_json(x) for x in created],
            "applications": [application_json(x) for x in applications]}
