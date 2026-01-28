from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from typing import Optional

from .database import engine, get_db
from .models import Base
from .routers import customers, transactions, rewards, analytics
from .auth import verify_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting LoyalSense API")
    Base.metadata.create_all(bind=engine)
    
    # Initialize AI models
    from .pattern_detection import PatternDetection
    app.state.pattern_detector = PatternDetection()
    
    yield
    
    # Shutdown
    logger.info("Shutting down LoyalSense API")

app = FastAPI(
    title="LoyalSense API",
    description="AI-Powered Customer Loyalty Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

# Include routers
app.include_router(
    customers.router,
    prefix="/api/v1/customers",
    tags=["customers"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    transactions.router,
    prefix="/api/v1/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    rewards.router,
    prefix="/api/v1/rewards",
    tags=["rewards"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)]
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to LoyalSense API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)