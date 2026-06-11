from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import SpimexTradingResult


async def get_last_trading_dates(
    db: AsyncSession,
    limit: int,
) -> list[date]:
    result = await db.execute(
        select(SpimexTradingResult.date)
        .distinct()
        .order_by(SpimexTradingResult.date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_trading_results_by_period(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    oil_id: str | None = None,
    delivery_type_id: str | None = None,
    delivery_basis_id: str | None = None,
) -> list[SpimexTradingResult]:
    query = (
        select(SpimexTradingResult)
        .where(SpimexTradingResult.date.between(start_date, end_date))
        .order_by(SpimexTradingResult.date.desc())
    )
    if oil_id is not None:
        query = query.where(SpimexTradingResult.oil_id == oil_id)
    if delivery_type_id is not None:
        query = query.where(SpimexTradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id is not None:
        query = query.where(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    result = (await db.execute(query)).scalars().all()
    return list(result)


async def get_last_trading_results(
    db: AsyncSession,
    oil_id: str | None = None,
    delivery_type_id: str | None = None,
    delivery_basis_id: str | None = None,
) -> list[SpimexTradingResult]:
    filters = []
    if oil_id is not None:
        filters.append(SpimexTradingResult.oil_id == oil_id)
    if delivery_type_id is not None:
        filters.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id is not None:
        filters.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    last_date_query = select(func.max(SpimexTradingResult.date)).where(*filters)

    last_date = (await db.execute(last_date_query)).scalar_one_or_none()

    if last_date is None:
        return []

    result_query = (
        select(SpimexTradingResult)
        .where(
            SpimexTradingResult.date == last_date,
            *filters,
        )
        .order_by(SpimexTradingResult.id.desc())
    )
    result = (await db.execute(result_query)).scalars().all()
    return list(result)
