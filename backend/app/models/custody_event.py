import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import CustodyEventType, OnChainStatus, UserRole


class ChainOfCustodyEvent(Base):
    """Immutable, append-only log of everything that happens to a batch.

    `id` is CLIENT-generated (a UUID minted on-device, possibly offline) and
    is the row's primary key, which is what makes /sync idempotent: replaying
    the same event twice is a no-op because the id already exists. Rows are
    never updated or deleted -- correcting a mistake means appending a new
    event (e.g. NOTE_ADDED), never rewriting history. That immutability is
    exactly the unit of data services.chain_hash (added alongside the web3.py
    integration) will hash and anchor on HarvestLedger.
    """

    __tablename__ = "custody_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    batch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("harvest_batches.id"), nullable=False, index=True)

    event_type: Mapped[CustodyEventType] = mapped_column(Enum(CustodyEventType, name="custody_event_type"), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # Snapshot of the actor's role at the time of the event, so the audit
    # trail still reads correctly even if a user's role is changed later.
    actor_role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)

    # When the action actually happened on-device (may be long before
    # `received_at` if the Farmer app was offline).
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Free-form event-specific data (weight_kg, quality_grade, price_per_kg,
    # notes, photo_url, gps coordinates, ...). Validated per event_type at
    # the Pydantic schema layer, stored schemaless here since the set of
    # fields varies by event type.
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    on_chain_status: Mapped[OnChainStatus] = mapped_column(
        Enum(OnChainStatus, name="on_chain_status"), default=OnChainStatus.PENDING, nullable=False
    )
    on_chain_tx_hash: Mapped[str | None] = mapped_column(String(66), nullable=True)
    on_chain_block_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
