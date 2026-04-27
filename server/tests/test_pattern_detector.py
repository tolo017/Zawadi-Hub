import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from db_models import Customer, Transaction
from services.pattern_detector import detect_patterns
import uuid
from datetime import datetime, timedelta, timezone

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def populate_seed():
    db = TestingSessionLocal()
    try:
        cust = Customer(id=uuid.uuid4(), name="Test Mango", email="test@test.com",
                        password_hash="hash", loyalty_card_number="LOYAL-TEST")
        db.add(cust)
        db.flush()
        now = datetime.now(timezone.utc)
        for i in range(4):
            tx = Transaction(customer_id=cust.id, items=["Mango Smoothie"], total_amount=5.0,
                             category="drink", points_earned=5, created_at=now - timedelta(days=10 - i))
            db.add(tx)
        db.commit()
        return cust.id
    finally:
        db.close()

def test_frequent_item_detection():
    setup_db()
    cust_id = populate_seed()
    db = TestingSessionLocal()
    try:
        patterns = detect_patterns(cust_id, db)
        assert len(patterns) >= 1
        assert patterns[0]["pattern_type"] == "frequent_item"
        assert patterns[0]["item"] == "Mango Smoothie"
        assert patterns[0]["discount_percent"] == 50
    finally:
        db.close()
        os.remove("./test.db")