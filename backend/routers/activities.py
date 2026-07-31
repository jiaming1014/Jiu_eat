"""活動相關 API 路由"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..common import activity_json, activity_or_404, application_json, member_or_404, taipei_now, validate_activity
from ..database import get_db

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("", response_model=List[schemas.Activity])
def list_activities(keyword: Optional[str] = None, category: Optional[str] = None,
                    city: Optional[str] = None, limit: int = Query(50, ge=1, le=100),
                    db: Session = Depends(get_db)):
    """取得活動列表：支援關鍵字搜尋、分類篩選、城市篩選"""
    query = db.query(models.Activity).filter_by(status="open").filter(models.Activity.activity_date > taipei_now())
    # 關鍵字搜尋：匹配活動名稱、說明、城市、地點、發起人名稱
    if keyword:
        like = f"%{keyword.strip()}%"
        subq = db.query(models.Member.id).filter(models.Member.display_name.ilike(like)).subquery()
        query = query.filter(or_(models.Activity.title.ilike(like), models.Activity.description.ilike(like), models.Activity.city.ilike(like), models.Activity.location_name.ilike(like), models.Activity.organizer_id.in_(subq)))
    if category: query = query.filter_by(category=category)  # 依分類篩選
    if city: query = query.filter(models.Activity.city.ilike(f"%{city.strip()}%"))  # 依城市篩選
    return [activity_json(x) for x in query.order_by(models.Activity.activity_date).limit(limit).all()]


@router.get("/{activity_id}", response_model=schemas.Activity)
def get_activity(activity_id: int, member_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """取得單一活動的詳細資料"""
    return activity_json(activity_or_404(db, activity_id), member_id=member_id)


@router.post("", response_model=schemas.Activity, status_code=201)
def create_activity(data: schemas.ActivityCreate, db: Session = Depends(get_db)):
    """建立新活動：驗證發起人存在、活動時間合理"""
    member_or_404(db, data.organizer_id); validate_activity(data)
    activity = models.Activity(**data.model_dump())
    db.add(activity); db.commit(); db.refresh(activity)
    return activity_json(activity)


@router.put("/{activity_id}", response_model=schemas.Activity)
def update_activity(activity_id: int, data: schemas.ActivityUpdate, db: Session = Depends(get_db)):
    """更新活動：僅限發起人可修改"""
    activity = activity_or_404(db, activity_id)
    if activity.organizer_id != data.organizer_id: raise HTTPException(403, "只有發起人可以修改活動")
    validate_activity(data)
    for key, value in data.model_dump().items(): setattr(activity, key, value)
    db.commit(); db.refresh(activity)
    return activity_json(activity)


@router.delete("/{activity_id}")
def delete_activity(activity_id: int, member_id: int, db: Session = Depends(get_db)):
    """刪除活動：僅限發起人可刪除"""
    activity = activity_or_404(db, activity_id)
    if activity.organizer_id != member_id: raise HTTPException(403, "只有發起人可以刪除活動")
    db.delete(activity); db.commit()
    return {"message": "活動已刪除"}


@router.post("/{activity_id}/applications", response_model=schemas.Application, status_code=201)
def apply(activity_id: int, data: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    """申請參加活動：檢查資格、防止重複申請"""
    activity = activity_or_404(db, activity_id); member_or_404(db, data.member_id)
    # 不能申請自己建立的活動
    if activity.organizer_id == data.member_id: raise HTTPException(400, "不能申請自己建立的活動")
    # 活動已停止報名或已截止
    if activity.status != "open" or activity.deadline <= taipei_now(): raise HTTPException(400, "活動已停止報名")
    # 檢查是否已申請過
    existing = db.query(models.Application).filter_by(activity_id=activity_id, member_id=data.member_id).first()
    if existing and existing.status != "cancelled": raise HTTPException(409, "你已經申請過這個活動")
    # 若之前已取消，重新申請（更新狀態為 pending）
    if existing:
        existing.status, existing.message, existing.created_at = "pending", data.message, taipei_now()
        application = existing
    else:
        application = models.Application(activity_id=activity_id, **data.model_dump()); db.add(application)
    db.commit(); db.refresh(application)
    return application_json(application)


@router.get("/{activity_id}/applications", response_model=List[schemas.Application])
def applications(activity_id: int, member_id: int, db: Session = Depends(get_db)):
    """查看活動的申請列表：僅限發起人可查看"""
    activity = activity_or_404(db, activity_id)
    if activity.organizer_id != member_id: raise HTTPException(403, "只有發起人可以查看申請")
    return [application_json(x) for x in activity.applications]


