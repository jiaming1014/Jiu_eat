import hashlib
import hmac
import os
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), 120_000
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except ValueError:
        return False


def member_or_404(db: Session, member_id: int):
    member = db.get(models.Member, member_id)
    if not member:
        raise HTTPException(404, "找不到會員")
    return member


def activity_or_404(db: Session, activity_id: int):
    activity = db.get(models.Activity, activity_id)
    if not activity:
        raise HTTPException(404, "找不到活動")
    return activity


def activity_json(activity: models.Activity) -> dict:
    approved = sum(x.status == "approved" for x in activity.applications)
    return {
        "id": activity.id, "organizer_id": activity.organizer_id,
        "organizer_name": activity.organizer.display_name, "title": activity.title,
        "description": activity.description, "category": activity.category,
        "city": activity.city, "location_name": activity.location_name,
        "activity_date": activity.activity_date, "deadline": activity.deadline,
        "max_participants": activity.max_participants, "approved_count": approved,
        "image_url": activity.image_url, "status": activity.status,
        "created_at": activity.created_at,
    }


def application_json(application: models.Application) -> dict:
    return {
        "id": application.id, "activity_id": application.activity_id,
        "member_id": application.member_id,
        "member_name": application.member.display_name,
        "activity_title": application.activity.title, "message": application.message,
        "status": application.status, "created_at": application.created_at,
    }


def validate_activity(data) -> None:
    if data.activity_date <= datetime.now():
        raise HTTPException(400, "活動時間必須晚於目前時間")
    if data.deadline >= data.activity_date:
        raise HTTPException(400, "報名截止時間必須早於活動時間")
