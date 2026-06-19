import pytest
from datetime import date
from unittest.mock import AsyncMock, Mock

from app.crud import (
    get_last_trading_dates,
    get_last_trading_results,
    get_trading_results_by_period,
)

pytestmark = pytest.mark.unit


def make_db_execute_mock(expected_results):
    scalars_mock = Mock()
    scalars_mock.all.return_value = expected_results
    result_mock = Mock()
    result_mock.scalars.return_value = scalars_mock
    db_mock = Mock()
    db_mock.execute = AsyncMock(return_value=result_mock)
    return db_mock, result_mock, scalars_mock


@pytest.mark.asyncio
async def test_get_last_trading_dates():
    expected_dates = [date(2025, 12, 10), date(2025, 12, 9)]
    db_mock, result_mock, scalars_mock = make_db_execute_mock(expected_dates)

    result = await get_last_trading_dates(db_mock, limit=2)

    assert result == expected_dates
    db_mock.execute.assert_awaited_once()
    result_mock.scalars.assert_called_once()
    scalars_mock.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_trading_results_by_period():
    expected_results = [Mock(), Mock()]
    db_mock, result_mock, scalars_mock = make_db_execute_mock(expected_results)

    result = await get_trading_results_by_period(
        db_mock,
        start_date=date(2025, 12, 9),
        end_date=date(2025, 12, 10),
    )

    assert result == expected_results
    db_mock.execute.assert_awaited_once()
    result_mock.scalars.assert_called_once()
    scalars_mock.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_last_trading_results():
    expected_results = [Mock(), Mock()]
    last_date_result_mock = Mock()
    last_date_result_mock.scalar_one_or_none.return_value = date(2025, 12, 9)
    scalars_mock = Mock()
    scalars_mock.all.return_value = expected_results
    rows_result_mock = Mock()
    rows_result_mock.scalars.return_value = scalars_mock
    db_mock = Mock()
    db_mock.execute = AsyncMock(side_effect=[last_date_result_mock, rows_result_mock])
    result = await get_last_trading_results(db_mock)

    assert result == expected_results
    assert db_mock.execute.await_count == 2
    last_date_result_mock.scalar_one_or_none.assert_called_once()
    rows_result_mock.scalars.assert_called_once()
    scalars_mock.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_last_trading_results_with_none_date():
    last_date_result_mock = Mock()
    last_date_result_mock.scalar_one_or_none.return_value = None
    db_mock = Mock()
    db_mock.execute = AsyncMock(return_value=last_date_result_mock)
    result = await get_last_trading_results(db_mock)

    assert result == []
    assert db_mock.execute.await_count == 1
    last_date_result_mock.scalar_one_or_none.assert_called_once()
