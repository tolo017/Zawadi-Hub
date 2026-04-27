from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_customer, Customer
from services.pattern_detector import detect_patterns
from models import PatternResult

router = APIRouter()

@router.get("/patterns", response_model=list[PatternResult])
def get_patterns(current_customer: Customer = Depends(get_current_customer),
                 db: Session = Depends(get_db)):
    patterns = detect_patterns(current_customer.id, db)
    result = []
    for p in patterns:
        result.append(PatternResult(
            pattern_type=p["pattern_type"],
            item=p.get("item"),
            combo_items=p.get("combo_items"),
            count=p["count"],
            suggested_reward_text=p["suggested_reward_text"],
            discount_percent=p["discount_percent"]
        ))
    return result