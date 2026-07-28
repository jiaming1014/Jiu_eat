from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..common import activity_json, application_json, member_or_404
from ..database import get_db

router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("/{member_id}", response_model=schemas.Member)
def get_member(member_id: int, db: Session = Depends(get_db)):
    return member_or_404(db, member_id)


@router.put("/{member_id}", response_model=schemas.Member)
def update_member(member_id: int, data: schemas.MemberUpdate, db: Session = Depends(get_db)):
    member = member_or_404(db, member_id)
    for key, value in data.model_dump().items():
        setattr(member, key, value.strip() if isinstance(value, str) else value)
    db.commit(); db.refresh(member)
    return member


@router.get("/{member_id}/activities")
def member_activities(member_id: int, db: Session = Depends(get_db)):
    member_or_404(db, member_id)
    created = db.query(models.Activity).filter_by(organizer_id=member_id).order_by(models.Activity.activity_date).all()
    applications = db.query(models.Application).filter_by(member_id=member_id).order_by(models.Application.created_at.desc()).all()
    return {"created": [activity_json(x) for x in created],
            "applications": [application_json(x) for x in applications]}
