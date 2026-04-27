from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_customer, Customer
from models import PointsResponse, TierInfo
from services.points_service import TIER_MULTIPLIERS, TIER_THRESHOLDS

router = APIRouter()

def get_tier_info(customer: Customer):
    total = float(customer.total_spent)
    current_tier = customer.tier
    next_tier = None
    next_spend = None
    for t, (low, high) in TIER_THRESHOLDS.items():
        if t == current_tier:
            if high:
                next_spend = high
                # find next tier name
                for nt, (nl,_) in TIER_THRESHOLDS.items():
                    if nl == next_spend:
                        next_tier = nt
                        break
            break
    if next_spend:
        progress = (total - TIER_THRESHOLDS[current_tier][0]) / (next_spend - TIER_THRESHOLDS[current_tier][0]) * 100
    else:
        progress = 100.0
        next_tier = None
    return TierInfo(
        current_tier=current_tier,
        next_tier=next_tier,
        total_spent=total,
        next_spend_goal=next_spend,
        progress_pct=min(progress, 100.0)
    )

@router.get("/points", response_model=PointsResponse)
def get_points(current_customer: Customer = Depends(get_current_customer),
               db: Session = Depends(get_db)):
    return PointsResponse(
        points_balance=current_customer.points_balance,
        tier=current_customer.tier,
        total_spent=float(current_customer.total_spent),
        tier_info=get_tier_info(current_customer)
    )