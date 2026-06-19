from datetime import date, datetime

import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from app.dependencies import get_db
from app.main import app


@pytest_asyncio.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def override_db():
    async def fake_db():
        yield None

    app.dependency_overrides[get_db] = fake_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def invalid_date_range():
    return {
        "start_date": "2025-12-10",
        "end_date": "2025-10-10",
    }


@pytest.fixture(scope="function")
def trading_dates():
    return [date(2025, 12, 10), date(2025, 12, 9)]


@pytest.fixture(scope="function")
def trading_dates_response():
    return {"dates": ["2025-12-10", "2025-12-09"]}


@pytest.fixture(scope="function")
def trading_dates_cache_json():
    return '{"dates": ["2025-12-10", "2025-12-09"]}'


@pytest.fixture(scope="function")
def trading_results():
    return [
        {
            "id": 1,
            "exchange_product_id": "fds",
            "exchange_product_name": "fdsa",
            "oil_id": "LOL",
            "delivery_basis_id": "A12",
            "delivery_basis_name": "CBA",
            "delivery_type_id": "A",
            "volume": 30,
            "total": 356,
            "count": 5,
            "date": date(2025, 12, 9),
            "created_on": datetime(2025, 12, 9, 10, 0, 0),
            "updated_on": datetime(2025, 12, 9, 10, 0, 0),
        }
    ]


@pytest.fixture(scope="function")
def trading_results_response():
    return [
        {
            "id": 1,
            "exchange_product_id": "fds",
            "exchange_product_name": "fdsa",
            "oil_id": "LOL",
            "delivery_basis_id": "A12",
            "delivery_basis_name": "CBA",
            "delivery_type_id": "A",
            "volume": "30",
            "total": "356",
            "count": 5,
            "date": "2025-12-09",
            "created_on": "2025-12-09T10:00:00",
            "updated_on": "2025-12-09T10:00:00",
        }
    ]
