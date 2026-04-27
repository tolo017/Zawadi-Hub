from sqlalchemy.orm import Session
from services.pattern_detector import detect_patterns
from db_models import Transaction
from typing import Dict

def generate_personalized_reward(customer_id: str, db: Session) -> Dict:
    # Check milestone: every 10 transactions -> free meal
    total_txns = db.query(Transaction).filter(
        Transaction.customer_id == customer_id
    ).count()
    if total_txns > 0 and total_txns % 10 == 0:
        return {
            "description": "🎉 Free Meal of your choice! 100% off any single item.",
            "discount_percent": 100,
            "item_target": "any item",
            "is_personalized": True
        }

    patterns = detect_patterns(customer_id, db)
    if patterns:
        pat = patterns[0]
        if pat["pattern_type"] == "frequent_item":
            return {
                "description": pat["suggested_reward_text"],
                "discount_percent": pat["discount_percent"],
                "item_target": pat["item"],
                "is_personalized": True
            }
        elif pat["pattern_type"] == "combo":
            return {
                "description": pat["suggested_reward_text"],
                "discount_percent": pat["discount_percent"],
                "item_target": None,
                "is_personalized": True
            }
    return {
        "description": "10% off your next order!",
        "discount_percent": 10,
        "item_target": None,
        "is_personalized": False
    }