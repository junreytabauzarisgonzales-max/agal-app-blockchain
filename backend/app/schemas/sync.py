from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

from app.schemas.batch import BatchCreate
from app.schemas.custody_event import CustodyEventCreate
from app.schemas.message import MessageCreate


class BatchCreatedSyncItem(BatchCreate):
    """A BATCH_CREATED event queued offline by the Farmer app."""

    type: Literal["batch_created"] = "batch_created"


class CustodyEventSyncItem(CustodyEventCreate):
    """Any other custody event queued offline by the Farmer app."""

    type: Literal["custody_event"] = "custody_event"


class MessageSyncItem(MessageCreate):
    """A chat message composed offline by the Farmer app."""

    type: Literal["message_sent"] = "message_sent"


SyncItem = Annotated[
    Union[BatchCreatedSyncItem, CustodyEventSyncItem, MessageSyncItem], Field(discriminator="type")
]


class SyncRequest(BaseModel):
    items: list[SyncItem]


class SyncItemResult(BaseModel):
    id: str
    type: Literal["batch_created", "custody_event", "message_sent"]
    status: Literal["created", "duplicate", "error"]
    detail: str | None = None


class SyncResponse(BaseModel):
    results: list[SyncItemResult]
