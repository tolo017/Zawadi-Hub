from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    Boolean, ForeignKey, JSON, Text, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class CustomerTier(enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String)
    date_of_birth = Column(DateTime)
    join_date = Column(DateTime, default=datetime.utcnow)
    total_points = Column(Integer, default=0)
    active_points = Column(Integer, default=0)
    customer_tier = Column(Enum(CustomerTier), default=CustomerTier.BRONZE)
    lifetime_value = Column(Float, default=0.0)
    preferred_categories = Column(JSON, default=list)
    behavior_pattern = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    transactions = relationship("Transaction", back_populates="customer")
    redemptions = relationship("Redemption", back_populates="customer")
    reward_preferences = relationship("RewardPreference", back_populates="customer")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    amount = Column(Float, nullable=False)
    points_earned = Column(Integer, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    category = Column(String)
    location = Column(String)
    items = Column(JSON)  # List of purchased items
    metadata = Column(JSON)  # Additional transaction data
    is_processed = Column(Boolean, default=True)
    
    customer = relationship("Customer", back_populates="transactions")

class Reward(Base):
    __tablename__ = "rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    points_required = Column(Integer, nullable=False)
    category = Column(String)  # discount, free_item, vip_access, etc.
    discount_percentage = Column(Float)
    discount_amount = Column(Float)
    expiry_date = Column(DateTime)
    stock_count = Column(Integer)
    is_active = Column(Boolean, default=True)
    redemption_count = Column(Integer, default=0)
    personalization_tags = Column(JSON, default=list)
    
    redemptions = relationship("Redemption", back_populates="reward")

class Redemption(Base):
    __tablename__ = "redemptions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    reward_id = Column(Integer, ForeignKey("rewards.id"))
    redemption_date = Column(DateTime, default=datetime.utcnow)
    points_used = Column(Integer, nullable=False)
    status = Column(String, default="completed")  # pending, completed, expired
    metadata = Column(JSON)
    
    customer = relationship("Customer", back_populates="redemptions")
    reward = relationship("Reward", back_populates="redemptions")

class RewardPreference(Base):
    __tablename__ = "reward_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    preferred_categories = Column(JSON, default=list)
    redemption_frequency = Column(String)  # frequent, occasional, rare
    point_accumulation_rate = Column(Float)  # Points per dollar
    personalized_offers = Column(Boolean, default=True)
    
    customer = relationship("Customer", back_populates="reward_preferences")

class PatternInsight(Base):
    __tablename__ = "pattern_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    pattern_type = Column(String)  # spending, temporal, category
    insight = Column(Text)
    confidence_score = Column(Float)
    detected_date = Column(DateTime, default=datetime.utcnow)
    recommended_actions = Column(JSON)
    
    customer = relationship("Customer")