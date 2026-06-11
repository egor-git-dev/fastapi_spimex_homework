from datetime import datetime, timedelta
import json
from typing import Any
import redis.asyncio as redis

from .config import settings

redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


def get_seconds_until_cache_reset(now: datetime | None = None) -> int:
    if now is None:
        now = datetime.now()
    reset_time = now.replace(
        hour=settings.cache_reset_hour,
        minute=settings.cache_reset_minute,
        second=0,
        microsecond=0,
    )
    if reset_time <= now:
        reset_time += timedelta(days=1)
    seconds_until_reset = (reset_time - now).total_seconds()
    return int(seconds_until_reset)


async def get_cache(key: str) -> Any | None:
    cached_value = await redis_client.get(key)

    if cached_value is None:
        return None
    return json.loads(cached_value)


async def set_cache(key: str, value: Any, ttl: int | None = None) -> None:
    json_value = json.dumps(value, ensure_ascii=False, default=str)
    if ttl is None:
        ttl = get_seconds_until_cache_reset()
    await redis_client.set(key, json_value, ex=ttl)


def build_cache_key(method: str, path: str, params: dict) -> str:
    filtered_params = {key: value for key, value in params.items() if value is not None}

    params_str = "&".join(
        f"{key}={value}" for key, value in sorted(filtered_params.items())
    )

    if params_str:
        return f"{method}:{path}?{params_str}"

    return f"{method}:{path}"
