"""
Redis message broker integration.
Publishes signals, audit events, and kill-switch triggers via Redis pub/sub.
In development mode, falls back gracefully when Redis is unavailable.
"""
import asyncio
import json
import logging
from typing import Optional, Callable, Any
from app.config import settings

logger = logging.getLogger(__name__)

_redis_client = None
_pubsub = None

CHANNELS = {
    "signals": "cryptosignal:signals",
    "audit": "cryptosignal:audit",
    "kill_switch": "cryptosignal:kill_switch",
    "prices": "cryptosignal:prices",
    "orders": "cryptosignal:orders",
}


async def get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis.asyncio as aioredis
        url = settings.redis_url
        password = settings.redis_password
        _redis_client = await aioredis.from_url(
            url,
            password=password,
            decode_responses=True,
            socket_connect_timeout=2,
        )
        await _redis_client.ping()
        logger.info("Redis connected: %s", url)
        return _redis_client
    except Exception as e:
        logger.warning("Redis unavailable — running without pub/sub: %s", e)
        return None


async def publish(channel_key: str, message: dict) -> bool:
    """Publish a message to a Redis channel. Returns False if Redis is unavailable."""
    redis = await get_redis()
    if redis is None:
        return False
    channel = CHANNELS.get(channel_key, channel_key)
    try:
        await redis.publish(channel, json.dumps(message))
        return True
    except Exception as e:
        logger.error("Redis publish failed: %s", e)
        return False


async def subscribe(channel_key: str, handler: Callable[[dict], Any]) -> None:
    """Subscribe to a Redis channel and call handler for each message."""
    redis = await get_redis()
    if redis is None:
        logger.warning("Cannot subscribe — Redis unavailable")
        return

    channel = CHANNELS.get(channel_key, channel_key)
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    await handler(data)
                except Exception as e:
                    logger.error("Channel handler error: %s", e)
    except asyncio.CancelledError:
        await pubsub.unsubscribe(channel)


async def publish_signal(signal: dict) -> None:
    await publish("signals", signal)


async def publish_audit(event: dict) -> None:
    await publish("audit", event)


async def publish_kill_switch(reason: str) -> None:
    await publish("kill_switch", {"event": "kill_switch", "reason": reason})
