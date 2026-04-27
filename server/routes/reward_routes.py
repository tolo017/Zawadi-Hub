from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import RewardOut
from auth import get_current_customer
from db_models import Customer, Reward, Redemption
from services.reward_service import generate_personalized_reward
from datetime import datetime, timedelta, timezone
import uuid

router = APIRouter()

@router.get("/suggest", response_model=RewardOut)
def suggest_reward(current_customer: Customer = Depends(get_current_customer),
                   db: Session = Depends(get_db)):
    reward_data = generate_personalized_reward(current_customer.id, db)
    reward = Reward(
        customer_id=current_customer.id,
        reward_description=reward_data["description"],
        discount_percent=reward_data["discount_percent"],
        item_target=reward_data.get("item_target"),
        is_personalized=reward_data.get("is_personalized", False),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return reward

@router.post("/redeem/{reward_id}")
def redeem(reward_id: uuid.UUID,
           current_customer: Customer = Depends(get_current_customer),
           db: Session = Depends(get_db)):
    reward = db.query(Reward).filter(Reward.id == reward_id, Reward.customer_id == current_customer.id).first()
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    if reward.redeemed:
        raise HTTPException(status_code=400, detail="Reward already redeemed")
    if reward.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reward expired")

    points_required = 20 if reward.is_personalized else 10
    if current_customer.points_balance < points_required:
        raise HTTPException(status_code=400, detail="Not enough points")

    current_customer.points_balance -= points_required
    reward.redeemed = True
    redemption = Redemption(reward_id=reward.id)
    db.add(redemption)
    db.commit()
    return {
        "message": f"Reward '{reward.reward_description}' redeemed!",
        "points_deducted": points_required,
        "new_balance": current_customer.points_balance
    }