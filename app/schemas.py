from datetime import datetime, date as date_type
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class TradingResultResponse(BaseModel):
    id: int
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: Decimal
    total: Decimal
    count: int
    date: date_type
    created_on: datetime
    updated_on: datetime

    model_config = ConfigDict(from_attributes=True)


class LastTradingDatesResponse(BaseModel):
    dates: list[date_type]
