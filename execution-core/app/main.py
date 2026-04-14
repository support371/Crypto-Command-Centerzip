"""
Execution Core — FastAPI main entry point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import account, positions, signals, orders, audit, health, guardian_relay, price_feed
from app.routers import settings as settings_router

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Execution Core starting — env=%s", settings.app_env)
    if settings.is_live and settings.ccxt_sandbox_mode:
        logger.warning("LIVE mode but CCXT sandbox is ON — verify intentional")
    yield
    logger.info("Execution Core shutting down")


app = FastAPI(
    title="CryptoSignal Execution Core",
    version="1.0.0",
    description="FastAPI execution core — paper trading, live execution, signal processing",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_live else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(account.router, prefix="/account", tags=["Account"])
app.include_router(positions.router, prefix="/positions", tags=["Positions"])
app.include_router(signals.router, prefix="/signals", tags=["Signals"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(audit.router, prefix="/audit", tags=["Audit"])
app.include_router(guardian_relay.router, prefix="/guardian", tags=["Guardian"])
app.include_router(price_feed.router, prefix="/price", tags=["Price Feed"])
app.include_router(settings_router.router, prefix="/settings", tags=["Settings"])
