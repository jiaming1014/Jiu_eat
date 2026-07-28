from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services.recommendation_service import recommend

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/{member_id}", response_model=List[schemas.Recommendation])
def recommendations(member_id: int, db: Session = Depends(get_db)):
    return recommend(member_id, db)
