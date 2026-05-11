"""Redis client for caching and task queues."""
import os
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for caching, pub/sub, and task queues."""

    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = None

    async def connect(self):
        try:
            import redis.asyncio as aioredis
            self.client = aioredis.from_url(self.url, decode_responses=True)
            await self.client.ping()
            logger.info("Redis connected")
        except ImportError:
            logger.warning("redis not installed, using mock mode")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        if self.client:
            return await self.client.get(key)
        return None

    async def set(self, key: str, value: str, ttl: int = 3600):
        if self.client:
            await self.client.set(key, value, ex=ttl)

    async def get_json(self, key: str) -> Optional[Dict]:
        data = await self.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None

    async def set_json(self, key: str, value: Any, ttl: int = 3600):
        await self.set(key, json.dumps(value, ensure_ascii=False, default=str), ttl)

    async def delete(self, key: str):
        if self.client:
            await self.client.delete(key)

    async def publish(self, channel: str, message: str):
        if self.client:
            await self.client.publish(channel, message)

    async def subscribe(self, channel: str):
        if self.client:
            pubsub = self.client.pubsub()
            await pubsub.subscribe(channel)
            return pubsub
        return None

    async def cache_analysis_result(self, analysis_id: str, result: Dict, ttl: int = 86400):
        await self.set_json(f"analysis:{analysis_id}:result", result, ttl)

    async def get_cached_analysis(self, analysis_id: str) -> Optional[Dict]:
        return await self.get_json(f"analysis:{analysis_id}:result")

    async def cache_whale_data(self, address: str, data: Dict, ttl: int = 3600):
        await self.set_json(f"whale:{address}", data, ttl)

    async def get_cached_whale(self, address: str) -> Optional[Dict]:
        return await self.get_json(f"whale:{address}")

    async def add_to_feed(self, event: Dict):
        """Add event to the real-time feed stream."""
        if self.client:
            await self.client.xadd("whale:feed", {"data": json.dumps(event, default=str)}, maxlen=1000)

    async def get_feed(self, last_id: str = "0", count: int = 50):
        """Get events from the feed stream."""
        if self.client:
            results = await self.client.xread({"whale:feed": last_id}, count=count, block=1000)
            events = []
            for stream, messages in results:
                for msg_id, data in messages:
                    events.append({"id": msg_id, "data": json.loads(data.get("data", "{}"))})
            return events
        return []
