import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import BatchStatus


class HarvestBatch(Base):
    """Current-state projection for a batch, derived by folding its events.

    The row's id is CLIENT-generated (set by the Farmer app at BATCH_CREATED
    time, offline) rather than server-assigned, so that creating a batch and
    replaying it through /sync is naturally idempotent. Every column here
    besides `id`, `farmer_id`, and `created_at` is a projection maintained by
    services.projection.apply_event() as new ChainOfCustodyEvent rows arrive
    -- never edited directly by a client request.
    """

    __tablename__ = "harvest_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    farmer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    species: Mapped[str] = mapped_column(String(255), nullable=False)
    estimated_weight_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(16), default="kg", nullable=False)
    # Captured automatically from the device's GPS at harvest time (see
    # apps/agal's create-batch screen) rather than typed in by the farmer.
    harvest_latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    harvest_longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    harvested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status: Mapped[BatchStatus] = mapped_column(
        Enum(BatchStatus, name="batch_status"), default=BatchStatus.HARVESTED, nullable=False
    )
    current_holder_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Bumped by the projection service each time an event is folded in;
    # lets clients cheaply detect "nothing changed since I last fetched".
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
