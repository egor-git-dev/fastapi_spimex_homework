import pytest

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_dynamics_without_required_dates(client):
    response = await client.get("/api/dynamics")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_dynamics_with_invalid_period(client, invalid_date_range):
    response = await client.get(
        "/api/dynamics",
        params=invalid_date_range,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_dynamics(
    monkeypatch,
    client,
    override_db,
    trading_results_response,
    trading_results,
):
    async def fake_get_cache(key: str):
        return None

    async def fake_set_cache(key: str, value, ttl=None):
        return None

    async def fake_get_trading_results_by_period(
        db,
        start_date,
        end_date,
        oil_id,
        delivery_type_id,
        delivery_basis_id,
    ):
        return trading_results

    monkeypatch.setattr(
        "app.main.get_cache",
        fake_get_cache,
    )
    monkeypatch.setattr(
        "app.main.get_trading_results_by_period",
        fake_get_trading_results_by_period,
    )
    monkeypatch.setattr(
        "app.main.set_cache",
        fake_set_cache,
    )

    response = await client.get(
        "/api/dynamics",
        params={"start_date": "2025-12-09", "end_date": "2025-12-10"},
    )
    assert response.status_code == 200
    assert response.json() == trading_results_response


@pytest.mark.asyncio
async def test_get_last_trading_dates(
    monkeypatch,
    client,
    override_db,
    trading_dates,
    trading_dates_response,
):
    async def fake_get_cache(key: str):
        return None

    async def fake_get_last_trading_dates(db, limit: int):
        return trading_dates

    async def fake_set_cache(key: str, value, ttl=None):
        return None

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

    response = await client.get(
        "/api/last-trading-dates",
        params={"limit": 2},
    )

    assert response.status_code == 200
    assert response.json() == trading_dates_response


@pytest.mark.asyncio
async def test_cache_hit(monkeypatch, client, override_db, trading_dates_response):
    async def fake_get_cache(key: str):
        return trading_dates_response

    async def fake_get_last_trading_dates(db, limit: int):
        raise AssertionError("CRUD should not be called on cache hit")

    async def fake_set_cache(key: str, value, ttl=None):
        raise AssertionError("set_cache should not be called on cache hit")

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

    response = await client.get(
        "/api/last-trading-dates",
        params={"limit": 2},
    )

    assert response.status_code == 200
    assert response.json() == trading_dates_response


@pytest.mark.asyncio
async def test_get_last_trading_results_endpoint(
    monkeypatch,
    client,
    override_db,
    trading_results_response,
    trading_results,
):
    async def fake_get_cache(key: str):
        return None

    async def fake_set_cache(key: str, value, ttl=None):
        return None

    async def fake_get_last_trading_results(
        db,
        oil_id,
        delivery_type_id,
        delivery_basis_id,
    ):
        return trading_results

    monkeypatch.setattr(
        "app.main.get_cache",
        fake_get_cache,
    )
    monkeypatch.setattr(
        "app.main.get_last_trading_results",
        fake_get_last_trading_results,
    )
    monkeypatch.setattr(
        "app.main.set_cache",
        fake_set_cache,
    )

    response = await client.get(
        "/api/trading-results",
        params={"oil_id": "OLID"},
    )
    assert response.status_code == 200
    assert response.json() == trading_results_response
