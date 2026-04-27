from collections import Counter
from datetime import datetime, timedelta, timezone
from itertools import combinations
from sqlalchemy.orm import Session
from db_models import Transaction

def detect_patterns(customer_id: str, db: Session):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    txns = db.query(Transaction).filter(
        Transaction.customer_id == customer_id,
        Transaction.created_at >= cutoff
    ).all()

    item_counter = Counter()
    for txn in txns:
        for item in txn.items:
            item_counter[item.lower()] += 1

    patterns = []
    for item, cnt in item_counter.items():
        if cnt >= 3:
            patterns.append({
                "pattern_type": "frequent_item",
                "item": item.title(),
                "count": cnt,
                "suggested_reward_text": f"You love {item.title()}s – get 50% off your next one!",
                "discount_percent": 50
            })

    pair_counter = Counter()
    for txn in txns:
        items_lower = sorted([i.lower() for i in txn.items])
        if len(items_lower) >= 2:
            for pair in combinations(items_lower, 2):
                pair_counter[tuple(pair)] += 1

    for (a, b), cnt in pair_counter.items():
        if cnt >= 2:
            combo_name = f"{a.title()} + {b.title()}"
            patterns.append({
                "pattern_type": "combo",
                "item": None,
                "combo_items": [a, b],
                "count": cnt,
                "suggested_reward_text": f"Combo Deal: {combo_name} – 30% off!",
                "discount_percent": 30
            })

    patterns.sort(key=lambda x: x["count"], reverse=True)
    return patterns