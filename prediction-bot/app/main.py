"""
Prediction Bot — Independent signal generation service.
Consumes market data from Redis, publishes signals to execution core via Redis.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.signal_generator import SignalGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

generator = SignalGenerator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Prediction Bot starting")
    await generator.start()
    yield
    await generator.stop()
    logger.info("Prediction Bot stopped")


app = FastAPI(title="CryptoSignal Prediction Bot", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "prediction-bot"}


@app.get("/status")
async def status():
    return {
        "running": generator.running,
        "signals_generated": generator.signals_generated,
        "last_signal": generator.last_signal,
    }
