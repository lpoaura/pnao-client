from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .config import DB_SCHEMA


class Base(DeclarativeBase):
    __abstract__ = True
    __table_args__ = {"schema": DB_SCHEMA}


class PnaoRawData(Base):
    __tablename__ = "raw_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_raw_data_payload_gin", "payload", postgresql_using="gin"),
        {"schema": DB_SCHEMA},
    )
