from datetime import date, datetime

import pytest
from httpx import AsyncClient, ASGITransport
from app.cache import build_cache_key, get_seconds_until_cache_reset
from app.dependencies import get_db
from app.main import app

transport = ASGITransport(app=app)


# ----------------------------------------API-------------------------------------------


@pytest.mark.asyncio
async def test_get_dynamics_without_required_dates():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/dynamics")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_dynamics_with_invalid_period():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/dynamics",
            params={"start_date": "2025-12-10", "end_date": "2025-11-10"},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_last_trading_dates(monkeypatch):
    async def fake_get_db():
        yield None

    async def fake_get_cache(key: str):
        return None

    async def fake_get_last_trading_dates(db, limit: int):
        return [
            date(2025, 12, 10),
            date(2025, 12, 9),
        ]

    async def fake_set_cache(key: str, value, ttl=None):
        return None

    app.dependency_overrides[get_db] = fake_get_db

    monkeypatch.setattr(
        "app.main.get_cache",
        fake_get_cache,
    )

    monkeypatch.setattr(
        "app.main.get_last_trading_dates",
        fake_get_last_trading_dates,
    )

    monkeypatch.setattr(
        "app.main.set_cache",
        fake_set_cache,
    )
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/last-trading-dates",
                params={"limit": 2},
            )
        assert response.status_code == 200
        assert response.json() == {
            "dates": [
                "2025-12-10",
                "2025-12-09",
            ]
        }
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cache_hit(monkeypatch):
    async def fake_get_db():
        yield None

    async def fake_get_cache(key: str):
        return {
            "dates": [
                "2025-12-10",
                "2025-12-09",
            ]
        }

    async def fake_get_last_trading_dates(db, limit: int):
        raise AssertionError("CRUD should not be called on cache hit")

    async def fake_set_cache(key: str, value, ttl=None):
        raise AssertionError("set_cache should not be called on cache hit")

    app.dependency_overrides[get_db] = fake_get_db

    monkeypatch.setattr(
        "app.main.get_cache",
        fake_get_cache,
    )

    monkeypatch.setattr(
        "app.main.get_last_trading_dates",
        fake_get_last_trading_dates,
    )

    monkeypatch.setattr(
        "app.main.set_cache",
        fake_set_cache,
    )
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/last-trading-dates",
                params={"limit": 2},
            )
        assert response.status_code == 200
        assert response.json() == {
            "dates": [
                "2025-12-10",
                "2025-12-09",
            ]
        }
    finally:
        app.dependency_overrides.clear()


# ---------------------------------------CACHE------------------------------------------


def test_build_cache_key():
    method = "GET"
    path = "/api/dynamics"

    params_1 = {
        "start_date": "2025-10-10",
        "end_date": "2025-12-10",
        "oil_id": None,
    }
    params_2 = {
        "oil_id": None,
        "end_date": "2025-12-10",
        "start_date": "2025-10-10",
    }
    result_1 = build_cache_key(method=method, path=path, params=params_1)
    result_2 = build_cache_key(method=method, path=path, params=params_2)
    assert result_1 == "GET:/api/dynamics?end_date=2025-12-10&start_date=2025-10-10"
    assert result_1 == result_2
    assert "oil_id" not in result_1
    assert result_1.startswith("GET:/api/dynamics")


def test_get_seconds_until_cache_reset():
    test_time_1 = datetime.fromisoformat("2025-12-10T13:00:00")
    test_time_2 = datetime.fromisoformat("2025-12-10T15:00:00")

    assert get_seconds_until_cache_reset(now=test_time_1) == 4260
    assert get_seconds_until_cache_reset(now=test_time_2) == 83460
