from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import CustomerCreate, CustomerOut, Token, LoginRequest
from auth import Customer, hash_password, verify_password, create_access_token, get_current_customer

router = APIRouter()

@router.post("/register", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def register(payload: CustomerCreate, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    customer = Customer(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.email == payload.email).first()
    if not customer or not verify_password(payload.password, customer.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(customer.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=CustomerOut)
def read_users_me(current_customer: Customer = Depends(get_current_customer)):
    return current_customer