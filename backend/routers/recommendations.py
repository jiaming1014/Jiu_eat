"""
推薦系統 API 路由（backend/routers/recommendations.py）
=======================================================
提供個人化活動推薦：
- GET /api/recommendations/{member_id}：根據會員興趣與居住地區推薦活動
實際的推薦演算法實作在 services/recommendation_service.py。
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services.recommendation_service import recommend    # 推薦演算法函式

# 建立路由器：所有端點以 /api/recommendations 為前綴，標記為 recommendations 群組
router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/{member_id}", response_model=List[schemas.Recommendation])
def recommendations(member_id: int, db: Session = Depends(get_db)):
    """
    根據會員興趣與居住地區推薦活動
    - 委派給 recommend() 取得依分數排序的推薦結果
    """
    return recommend(member_id, db)
