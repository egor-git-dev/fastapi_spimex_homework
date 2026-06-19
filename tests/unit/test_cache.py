from datetime import datetime
import pytest

from app.cache import (
    build_cache_key,
    get_cache,
    set_cache,
    get_seconds_until_cache_reset,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def redis_set_spy(monkeypatch):
    called = {}

    async def fake_redis_set(key, json_value, ex=None):
        called["key"] = key
        called["value"] = json_value
        called["ex"] = ex

    monkeypatch.setattr("app.cache.redis_client.set", fake_redis_set)

    return called


@pytest.mark.parametrize(
    "params, expected_key",
    [
        (
            {"start_date": "2025-10-10", "end_date": "2025-12-10", "oil_id": None},
            "GET:/api/dynamics?end_date=2025-12-10&start_date=2025-10-10",
        ),
        (
            {},
            "GET:/api/dynamics",
        ),
        (
            {"start_date": None, "end_date": None, "oil_id": None},
            "GET:/api/dynamics",
        ),
    ],
)
def test_build_cache_key(params, expected_key):
    method = "GET"
    path = "/api/dynamics"
    result = build_cache_key(method=method, path=path, params=params)
    assert result == expected_key


def test_build_same_key_different_order():
    method = "GET"
    path = "/api/dynamics"
    params1 = {"start_date": "2025-10-10", "end_date": "2025-12-10"}
    params2 = {"end_date": "2025-12-10", "start_date": "2025-10-10"}
    key1 = build_cache_key(method=method, path=path, params=params1)
    key2 = build_cache_key(method=method, path=path, params=params2)
    assert key1 == key2


@pytest.mark.parametrize(
    "now, expected_ttl",
    [
        (datetime.fromisoformat("2025-12-10T13:00:00"), 4260),
        (datetime.fromisoformat("2025-12-10T15:00:00"), 83460),
    ],
)
def test_get_seconds_until_cache_reset(now: datetime, expected_ttl: int):
    assert get_seconds_until_cache_reset(now=now) == expected_ttl


@pytest.mark.asyncio
async def test_get_cache_returns_none(monkeypatch):
    async def fake_redis_get(key: str):
        return None

    monkeypatch.setattr(
        "app.cache.redis_client.get",
        fake_redis_get,
    )

    result = await get_cache("some-key")

    assert result is None


@pytest.mark.asyncio
async def test_get_cache_returns_json(
    monkeypatch, trading_dates_response, trading_dates_cache_json
):
    async def fake_redis_get(key: str):
        return trading_dates_cache_json

    monkeypatch.setattr(
        "app.cache.redis_client.get",
        fake_redis_get,
    )

    result = await get_cache("some-key")

    assert result == trading_dates_response


@pytest.mark.asyncio
async def test_set_cache_with_ttl(redis_set_spy):
    await set_cache("some-key", {"message": "Hello World"}, ttl=60)

    assert redis_set_spy["key"] == "some-key"
    assert redis_set_spy["value"] == '{"message": "Hello World"}'
    assert redis_set_spy["ex"] == 60


@pytest.mark.asyncio
async def test_set_cache_without_ttl(monkeypatch, redis_set_spy):
    def fake_get_seconds_until_cache_reset():
        return 123

    monkeypatch.setattr(
        "app.cache.get_seconds_until_cache_reset",
        fake_get_seconds_until_cache_reset,
    )

    await set_cache("some-key", {"message": "Hello World"})

    assert redis_set_spy["key"] == "some-key"
    assert redis_set_spy["value"] == '{"message": "Hello World"}'
    assert redis_set_spy["ex"] == 123
