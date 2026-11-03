import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import UserRole
from app.schemas.common import as_utc


class MessageCreate(BaseModel):
    """Shape of a message, whether it arrives via /sync or POST /messages directly."""

    id: uuid.UUID
    recipient_id: uuid.UUID
    body: str = Field(min_length=1, max_length=10000)
    occurred_at: datetime

    _utc = field_validator("occurred_at")(as_utc)

    @field_validator("body")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message must not be blank")
        return value


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sender_id: uuid.UUID
    recipient_id: uuid.UUID
    body: str
    occurred_at: datetime
    received_at: datetime
    read_at: datetime | None


class ThreadSummary(BaseModel):
    """One row in a user's chat inbox: who the thread is with, and a preview."""

    counterpart_id: uuid.UUID
    counterpart_name: str
    counterpart_role: UserRole
    counterpart_phone_number: str | None
    last_message_body: str
    last_message_at: datetime
    unread_count: int
