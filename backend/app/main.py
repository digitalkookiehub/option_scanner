import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, close_db, populate_stocks
from app.core.constants import STOCK_LIST
from app.routers import auth, screening, market_data, options, orders, stocks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await populate_stocks(STOCK_LIST)
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="NSE Stock Screener API",
    description="Ichimoku Cloud + MACD stock screening with Upstox integration",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow React dev server + Vercel production
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
if os.environ.get("FRONTEND_URL"):
    allowed_origins.append(os.environ["FRONTEND_URL"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(screening.router)
app.include_router(market_data.router)
app.include_router(options.router)
app.include_router(orders.router)
app.include_router(stocks.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "stock-screener-api"}
