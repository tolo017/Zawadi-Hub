from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
import uuid

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class CustomerOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    loyalty_card_number: str
    points_balance: int
    tier: str
    total_spent: float
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TransactionCreate(BaseModel):
    items: List[str]
    total_amount: float
    category: str = 'food'   # 'drink', 'food', 'combo'

    @field_validator('category')
    def validate_category(cls, v):
        if v not in ('drink', 'food', 'combo'):
            raise ValueError('Category must be drink, food, or combo')
        return v

class TransactionOut(BaseModel):
    id: uuid.UUID
    items: List[str]
    total_amount: float
    category: str
    points_earned: int
    created_at: datetime

    class Config:
        from_attributes = True

class RewardOut(BaseModel):
    id: uuid.UUID
    reward_description: str
    discount_percent: int
    item_target: Optional[str] = None
    is_personalized: bool
    expires_at: datetime
    redeemed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PatternResult(BaseModel):
    pattern_type: str
    item: Optional[str] = None
    combo_items: Optional[List[str]] = None
    count: int
    suggested_reward_text: str
    discount_percent: int

class TierInfo(BaseModel):
    current_tier: str
    next_tier: Optional[str]
    total_spent: float
    next_spend_goal: Optional[float]
    progress_pct: float

class PointsResponse(BaseModel):
    points_balance: int
    tier: str
    total_spent: float
    tier_info: TierInfo