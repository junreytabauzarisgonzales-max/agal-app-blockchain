import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Message(Base):
    """A direct message between two accounts (any mix of Farmer, Supplier,
    Buyer). Immutable and append-only, exactly like ChainOfCustodyEvent --
    `id` is client-generated, which is what makes both the direct
    POST /messages path and the Farmer app's offline /sync path idempotent.
    There's no separate "conversation" row: a thread between two users is
    just every Message where they're the sender/recipient pair.
    """

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    recipient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
