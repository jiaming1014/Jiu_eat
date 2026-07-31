"""活動申請狀態管理 API 路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..common import application_json
from ..database import get_db

router = APIRouter(prefix="/api/applications", tags=["applications"])


def change_status(application_id: int, member_id: int, status: str, db: Session):
    """
    變更申請狀態的共用函式
    - cancelled：僅限申請人自己取消
    - approved/rejected：僅限活動發起人審核
    - approved 時會檢查活動名額是否已滿
    """
    application = db.get(models.Application, application_id)
    if not application: raise HTTPException(404, "找不到申請")
    # 權限檢查
    if status == "cancelled":
        if application.member_id != member_id: raise HTTPException(403, "只能取消自己的申請")
    elif application.activity.organizer_id != member_id:
        raise HTTPException(403, "只有發起人可以審核")
    # 核准時檢查名額
    if status == "approved":
        count = db.query(models.Application).filter_by(activity_id=application.activity_id, status="approved").count()
        if count >= application.activity.max_participants: raise HTTPException(400, "活動名額已滿")
    application.status = status; db.commit(); db.refresh(application)
    return application_json(application)


@router.put("/{application_id}/approve", response_model=schemas.Application)
def approve(application_id: int, member_id: int, db: Session = Depends(get_db)):
    """核准申請"""
    return change_status(application_id, member_id, "approved", db)


@router.put("/{application_id}/reject", response_model=schemas.Application)
def reject(application_id: int, member_id: int, db: Session = Depends(get_db)):
    """拒絕申請"""
    return change_status(application_id, member_id, "rejected", db)


@router.put("/{application_id}/cancel", response_model=schemas.Application)
def cancel(application_id: int, member_id: int, db: Session = Depends(get_db)):
    """取消申請"""
    return change_status(application_id, member_id, "cancelled", db)
