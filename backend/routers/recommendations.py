"""推薦系統 API 路由"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services.recommendation_service import recommend

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/{member_id}", response_model=List[schemas.Recommendation])
def recommendations(member_id: int, db: Session = Depends(get_db)):
    """根據會員興趣與居住地區推薦活動"""
    return recommend(member_id, db)
