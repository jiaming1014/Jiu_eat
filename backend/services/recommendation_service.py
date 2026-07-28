from datetime import datetime

from sqlalchemy.orm import Session

from .. import models
from ..common import activity_json, member_or_404


def recommend(member_id: int, db: Session) -> list[dict]:
    """Rule-based baseline. Replace this body with ML inference later."""
    member = member_or_404(db, member_id)
    applied_ids = {x.activity_id for x in member.applications if x.status != "cancelled"}
    interests = {x.strip().lower() for x in member.interests.split(",") if x.strip()}
    results = []
    for activity in db.query(models.Activity).filter_by(status="open").all():
        if activity.organizer_id == member_id or activity.id in applied_ids or activity.deadline <= datetime.now():
            continue
        score, reasons = 20, ["目前仍可報名"]
        if activity.category.lower() in interests:
            score += 50; reasons.append("符合你的興趣")
        if member.city and member.city.lower() in activity.city.lower():
            score += 30; reasons.append("位於你的常用地區")
        results.append({**activity_json(activity), "score": score, "reasons": reasons})
    return sorted(results, key=lambda x: (-x["score"], x["activity_date"]))