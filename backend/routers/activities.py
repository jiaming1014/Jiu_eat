from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..common import activity_json, activity_or_404, application_json, member_or_404, validate_activity
from ..database import get_db

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("", response_model=List[schemas.Activity])
def list_activities(keyword: Optional[str] = None, category: Optional[str] = None,
                    city: Optional[str] = None, limit: int = Query(50, ge=1, le=100),
                    db: Session = Depends(get_db)):
    query = db.query(models.Activity).filter_by(status="open")
    if keyword:
        like = f"%{keyword.strip()}%"
        query = query.filter(or_(models.Activity.title.ilike(like), models.Activity.description.ilike(like)))
    if category: query = query.filter_by(category=category)
    if city: query = query.filter(models.Activity.city.ilike(f"%{city.strip()}%"))
    return [activity_json(x) for x in query.order_by(models.Activity.activity_date).limit(limit).all()]


@router.get("/{activity_id}", response_model=schemas.Activity)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    return activity_json(activity_or_404(db, activity_id))


@router.post("", response_model=schemas.Activity, status_code=201)
def create_activity(data: schemas.ActivityCreate, db: Session = Depends(get_db)):
    member_or_404(db, data.organizer_id); validate_activity(data)
    activity = models.Activity(**data.model_dump())
    db.add(activity); db.commit(); db.refresh(activity)
    return activity_json(activity)


@router.put("/{activity_id}", response_model=schemas.Activity)
def update_activity(activity_id: int, data: schemas.ActivityUpdate, db: Session = Depends(get_db)):
    activity = activity_or_404(db, activity_id)
    if activity.organizer_id != data.organizer_id: raise HTTPException(403, "只有發起人可以修改活動")
    validate_activity(data)
    for key, value in data.model_dump().items(): setattr(activity, key, value)
    db.commit(); db.refresh(activity)
    return activity_json(activity)


@router.delete("/{activity_id}")
def delete_activity(activity_id: int, member_id: int, db: Session = Depends(get_db)):
    activity = activity_or_404(db, activity_id)
    if activity.organizer_id != member_id: raise HTTPException(403, "只有發起人可以刪除活動")
    db.delete(activity); db.commit()
    return {"message": "活動已刪除"}


@router.post("/{activity_id}/applications", response_model=schemas.Application, status_code=201)
def apply(activity_id: int, data: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    activity = activity_or_404(db, activity_id); member_or_404(db, data.member_id)
    if activity.organizer_id == data.member_id: raise HTTPException(400, "不能申請自己建立的活動")
    if activity.status != "open" or activity.deadline <= datetime.now(): raise HTTPException(400, "活動已停止報名")
    existing = db.query(models.Application).filter_by(activity_id=activity_id, member_id=data.member_id).first()
    if existing and existing.status != "cancelled": raise HTTPException(409, "你已經申請過這個活動")
    if existing:
        existing.status, existing.message, existing.created_at = "pending", data.message, datetime.utcnow()
        application = existing
    else:
        application = models.Application(activity_id=activity_id, **data.model_dump()); db.add(application)
    db.commit(); db.refresh(application)
    return application_json(application)


@router.get("/{activity_id}/applications", response_model=List[schemas.Application])
def applications(activity_id: int, member_id: int, db: Session = Depends(get_db)):
    activity = activity_or_404(db, activity_id)
    if activity.organizer_id != member_id: raise HTTPException(403, "只有發起人可以查看申請")
    return [application_json(x) for x in activity.applications]
