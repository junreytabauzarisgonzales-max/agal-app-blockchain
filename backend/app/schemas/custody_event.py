import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import CustodyEventType, OnChainStatus, UserRole
from app.schemas.common import as_utc


class CustodyEventCreate(BaseModel):
    """Shape of a custody-event item, whether it arrives via /sync or POST /custody-events directly."""

    id: uuid.UUID
    batch_id: uuid.UUID
    event_type: CustodyEventType
    occurred_at: datetime
    payload: dict[str, Any] = Field(default_factory=dict)

    _utc = field_validator("occurred_at")(as_utc)


class CustodyEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    batch_id: uuid.UUID
    event_type: CustodyEventType
    actor_id: uuid.UUID
    actor_role: UserRole
    occurred_at: datetime
    received_at: datetime
    payload: dict[str, Any]
    on_chain_status: OnChainStatus
    on_chain_tx_hash: str | None
    on_chain_block_number: int | None


class CustodyEventVerification(BaseModel):
    """Result of independently checking one event against the live
    HarvestLedger contract on Sepolia -- not just trusting the backend's
    own `on_chain_status` column, but recomputing the hash and comparing
    it against what the chain itself currently reports.
    """

    event_id: uuid.UUID
    on_chain_exists: bool
    verified: bool  # on_chain_exists AND the recomputed hash matches
    expected_data_hash: str
    on_chain_data_hash: str | None
    on_chain_recorded_at: datetime | None
    tx_hash: str | None
