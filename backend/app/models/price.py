import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PriceRecord(Base):
    """A price point published by a supplier or buyer (posted while online).

    Unlike batches/custody events, price records don't go through the
    offline sync queue -- Supplier and Buyer roles assume normal
    connectivity, so this is a plain server-assigned-id CRUD row.
    """

    __tablename__ = "price_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    species: Mapped[str] = mapped_column(String(255), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(64), nullable=True)
    price_per_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PHP", nullable=False)
    municipality: Mapped[str | None] = mapped_column(String(255), nullable=True)
    posted_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
