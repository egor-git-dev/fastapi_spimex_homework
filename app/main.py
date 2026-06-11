from datetime import date
import logging

from fastapi import FastAPI, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession


from .dependencies import get_db
from .crud import (
    get_last_trading_dates,
    get_trading_results_by_period,
    get_last_trading_results,
)
from .schemas import TradingResultResponse, LastTradingDatesResponse
from .cache import build_cache_key, get_cache, set_cache

app = FastAPI()

logger = logging.getLogger("uvicorn.error")


@app.get(
    "/api/last-trading-dates",
    summary="Список дат последних торговых дней",
    response_model=LastTradingDatesResponse,
)
async def get_last_trading_dates_endpoint(
    request: Request,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=10, ge=1, le=100),
) -> LastTradingDatesResponse:
    cache_key = build_cache_key(
        method=request.method,
        path=request.url.path,
        params={"limit": limit},
    )
    cached_value = await get_cache(cache_key)

    if cached_value is not None:
        logger.info("Cache hit: %s", cache_key)
        return LastTradingDatesResponse.model_validate(cached_value)

    logger.info("Cache miss: %s", cache_key)
    dates = await get_last_trading_dates(db=db, limit=limit)
    response = LastTradingDatesResponse(dates=dates)
    await set_cache(
        cache_key,
        response.model_dump(mode="json"),
    )
    return response


@app.get(
    "/api/dynamics",
    summary="Список торгов за заданный период",
    response_model=list[TradingResultResponse],
)
async def get_dynamics(
    request: Request,
    start_date: date,
    end_date: date,
    oil_id: str | None = Query(default=None, max_length=4),
    delivery_type_id: str | None = Query(default=None, max_length=1),
    delivery_basis_id: str | None = Query(default=None, max_length=3),
    db: AsyncSession = Depends(get_db),
) -> list[TradingResultResponse]:
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid period"
        )
    cache_key = build_cache_key(
        method=request.method,
        path=request.url.path,
        params={
            "start_date": start_date,
            "end_date": end_date,
            "oil_id": oil_id,
            "delivery_type_id": delivery_type_id,
            "delivery_basis_id": delivery_basis_id,
        },
    )
    cached_value = await get_cache(cache_key)

    if cached_value is not None:
        logger.info("Cache hit: %s", cache_key)
        results = []
        for value in cached_value:
            results.append(TradingResultResponse.model_validate(value))
        return results

    logger.info("Cache miss: %s", cache_key)
    results = await get_trading_results_by_period(
        db=db,
        start_date=start_date,
        end_date=end_date,
        oil_id=oil_id,
        delivery_type_id=delivery_type_id,
        delivery_basis_id=delivery_basis_id,
    )
    response = []
    for result in results:
        response.append(TradingResultResponse.model_validate(result))

    await set_cache(
        cache_key,
        [item.model_dump(mode="json") for item in response],
    )
    return response


@app.get(
    "/api/trading-results",
    summary="Список последних торгов",
    response_model=list[TradingResultResponse],
)
async def get_last_trading_results_endpoint(
    request: Request,
    oil_id: str | None = Query(default=None, max_length=4),
    delivery_type_id: str | None = Query(default=None, max_length=1),
    delivery_basis_id: str | None = Query(default=None, max_length=3),
    db: AsyncSession = Depends(get_db),
) -> list[TradingResultResponse]:
    cache_key = build_cache_key(
        method=request.method,
        path=request.url.path,
        params={
            "oil_id": oil_id,
            "delivery_type_id": delivery_type_id,
            "delivery_basis_id": delivery_basis_id,
        },
    )
    cached_value = await get_cache(cache_key)

    if cached_value is not None:
        logger.info("Cache hit: %s", cache_key)
        results = [
            TradingResultResponse.model_validate(value) for value in cached_value
        ]
        return results

    logger.info("Cache miss: %s", cache_key)
    results = await get_last_trading_results(
        db=db,
        oil_id=oil_id,
        delivery_type_id=delivery_type_id,
        delivery_basis_id=delivery_basis_id,
    )
    response = [TradingResultResponse.model_validate(value) for value in results]
    await set_cache(
        cache_key,
        [item.model_dump(mode="json") for item in response],
    )
    return response
