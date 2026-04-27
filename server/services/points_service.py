from typing import Dict, Optional, Tuple

TIER_MULTIPLIERS = {
    'bronze': 1.0,
    'silver': 1.2,
    'gold': 1.5,
    'platinum': 2.0
}

# (low inclusive, high exclusive) – high None means unbounded
TIER_THRESHOLDS: Dict[str, Tuple[float, Optional[float]]] = {
    'bronze': (0, 100),
    'silver': (100, 300),
    'gold': (300, 500),
    'platinum': (500, None)
}

CATEGORY_BONUSES = {
    'drink': 5,
    'food': 3,
    'combo': 10
}

def calculate_points(total_amount: float, category: str, tier: str) -> int:
    multiplier = TIER_MULTIPLIERS.get(tier, 1.0)
    base = int(total_amount * multiplier)
    bonus = CATEGORY_BONUSES.get(category, 0)
    return base + bonus