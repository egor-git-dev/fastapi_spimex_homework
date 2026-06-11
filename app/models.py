from datetime import datetime, date as date_type
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class SpimexTradingResult(Base):
    __tablename__ = "spimex_trading_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    exchange_product_id: Mapped[str] = mapped_column(String(length=20))
    exchange_product_name: Mapped[str] = mapped_column(String(length=255))
    oil_id: Mapped[str] = mapped_column(String(length=4))
    delivery_basis_id: Mapped[str] = mapped_column(String(length=3))
    delivery_basis_name: Mapped[str] = mapped_column(String(length=255))
    delivery_type_id: Mapped[str] = mapped_column(String(length=1))
    volume: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    count: Mapped[int] = mapped_column(Integer)
    date: Mapped[date_type] = mapped_column(Date)
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    updated_on: Mapped[datetime] = mapped_column(DateTime(timezone=False))
