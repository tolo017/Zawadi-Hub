import uuid
import secrets
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, UUID, ForeignKey, JSON, Numeric, CheckConstraint
from database import Base
from datetime import datetime, timezone

class Customer(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    loyalty_card_number = Column(
        String(20), unique=True, nullable=False,
        default=lambda: f"LOYAL-{secrets.token_hex(4).upper()}"
    )
    points_balance = Column(Integer, default=0)
    tier = Column(String(20), nullable=False, default='bronze')
    total_spent = Column(Numeric(10,2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    items = Column(JSON, nullable=False)
    total_amount = Column(Numeric(10,2), nullable=False)
    category = Column(String(10), nullable=False, default='food')
    points_earned = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Reward(Base):
    __tablename__ = "rewards"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    reward_description = Column(String, nullable=False)
    discount_percent = Column(Integer, nullable=False)
    item_target = Column(String, nullable=True)
    is_personalized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    redeemed = Column(Boolean, default=False)

class Redemption(Base):
    __tablename__ = "redemptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reward_id = Column(UUID(as_uuid=True), ForeignKey("rewards.id"), nullable=False)
    redeemed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))