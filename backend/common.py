"""共用工具函式：密碼雜湊、資料驗證、JSON 轉換"""

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

# 台北時區（UTC+8）
tz_taipei = timezone(timedelta(hours=8), "Asia/Taipei")


def taipei_now():
    """取得當前台北時間（naive datetime）"""
    return datetime.now(tz_taipei).replace(tzinfo=None)


def to_naive_taipei(dt):
    """將 timezone-aware datetime 轉換為台北時區的 naive datetime"""
    if isinstance(dt, datetime) and dt.tzinfo is not None:
        return dt.astimezone(tz_taipei).replace(tzinfo=None)
    return dt


from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models


# ── 密碼雜湊 ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    """使用 PBKDF2-SHA256 雜湊密碼，回傳 salt:digest 格式"""
    salt = os.urandom(16)                                # 隨機產生 16 bytes 鹽值
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{salt.hex()}:{digest.hex()}"                # 格式：hex(salt):hex(digest)


def verify_password(password: str, stored: str) -> bool:
    """驗證密碼是否與儲存的雜湊值匹配"""
    try:
        salt_hex, digest_hex = stored.split(":", 1)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), 120_000
        )
        return hmac.compare_digest(digest.hex(), digest_hex)  # 防止時序攻擊
    except ValueError:
        return False


# ── 資料查詢輔助 ──────────────────────────────────────────

def member_or_404(db: Session, member_id: int):
    """查詢會員，找不到則回傳 404 錯誤"""
    member = db.get(models.Member, member_id)
    if not member:
        raise HTTPException(404, "找不到會員")
    return member


def activity_or_404(db: Session, activity_id: int):
    """查詢活動，找不到則回傳 404 錯誤"""
    activity = db.get(models.Activity, activity_id)
    if not activity:
        raise HTTPException(404, "找不到活動")
    return activity


# ── JSON 轉換 ─────────────────────────────────────────────

def activity_json(activity: models.Activity, member_id: Optional[int] = None) -> dict:
    """將 Activity ORM 物件轉換為 API 回應用的 dict"""
    approved = sum(x.status == "approved" for x in activity.applications)  # 統計已核准人數
    result = {
        "id": activity.id, "organizer_id": activity.organizer_id,
        "organizer_name": activity.organizer.display_name, "title": activity.title,
        "description": activity.description, "category": activity.category,
        "city": activity.city, "location_name": activity.location_name,
        "activity_date": activity.activity_date, "deadline": activity.deadline,
        "max_participants": activity.max_participants, "approved_count": approved,
        "image_url": activity.image_url, "status": activity.status,
        "created_at": activity.created_at,
    }
    result["my_application_id"] = None
    result["my_application_status"] = None
    if member_id:
        app = next((a for a in activity.applications if a.member_id == member_id), None)
        if app:
            result["my_application_id"] = app.id
            result["my_application_status"] = app.status
    return result


def application_json(application: models.Application) -> dict:
    """將 Application ORM 物件轉換為 API 回應用的 dict"""
    return {
        "id": application.id, "activity_id": application.activity_id,
        "member_id": application.member_id,
        "member_name": application.member.display_name,
        "activity_title": application.activity.title, "message": application.message,
        "status": application.status, "created_at": application.created_at,
    }


# ── 活動資料驗證 ──────────────────────────────────────────

def validate_activity(data) -> None:
    """驗證活動時間與截止時間的合理性"""
    ad = to_naive_taipei(data.activity_date)
    dl = to_naive_taipei(data.deadline)
    if ad <= taipei_now():
        raise HTTPException(400, "活動時間必須晚於目前時間")
    if dl >= ad:
        raise HTTPException(400, "報名截止時間必須早於活動時間")
