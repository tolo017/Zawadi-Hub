from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import TransactionCreate, TransactionOut
from auth import get_current_customer
from db_models import Customer, Transaction
from services.points_service import calculate_points, TIER_THRESHOLDS
from decimal import Decimal

router = APIRouter()

@router.post("", response_model=TransactionOut)
def create_transaction(payload: TransactionCreate,
                       current_customer: Customer = Depends(get_current_customer),
                       db: Session = Depends(get_db)):
    points_earned = calculate_points(payload.total_amount, payload.category, current_customer.tier)
    transaction = Transaction(
        customer_id=current_customer.id,
        items=payload.items,
        total_amount=payload.total_amount,
        category=payload.category,
        points_earned=points_earned,
    )
    current_customer.points_balance += points_earned
    current_customer.total_spent += Decimal(str(payload.total_amount))

    # Recalculate tier based on total_spent
    new_tier = 'bronze'
    for tier, (low, high) in TIER_THRESHOLDS.items():
        if current_customer.total_spent >= low and (high is None or current_customer.total_spent < high):
            new_tier = tier
            break
    current_customer.tier = new_tier

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("", response_model=list[TransactionOut])
def list_transactions(current_customer: Customer = Depends(get_current_customer),
                      db: Session = Depends(get_db)):
    return db.query(Transaction).filter(
        Transaction.customer_id == current_customer.id
    ).order_by(Transaction.created_at.desc()).limit(10).all()

@router.get("/count")
def transaction_count(current_customer: Customer = Depends(get_current_customer),
                      db: Session = Depends(get_db)):
    total = db.query(Transaction).filter(Transaction.customer_id == current_customer.id).count()
    return {"count": total}