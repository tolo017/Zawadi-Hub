from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routes import auth_routes, transaction_routes, reward_routes, analytics_routes, points_routes

app = FastAPI(title="Runas Zawadihub – FlavorPrint Loyalty")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# API routes first
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(transaction_routes.router, prefix="/transactions", tags=["Transactions"])
app.include_router(reward_routes.router, prefix="/rewards", tags=["Rewards"])
app.include_router(analytics_routes.router, prefix="/analytics", tags=["Analytics"])
app.include_router(points_routes.router, tags=["Points"])

# Static file mount at the end
import os
static_dir = "/client"   # <-- must match the volume mount
if not os.path.exists(static_dir):
    raise RuntimeError(f"Static directory '{static_dir}' does not exist")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")