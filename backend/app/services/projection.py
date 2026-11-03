"""Apply authorized, append-only events to the batch read model."""
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch import HarvestBatch
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import BatchStatus, CustodyEventType, UserRole
from app.models.user import User
from app.schemas.batch import BatchCreate
from app.schemas.common import as_utc
from app.schemas.custody_event import CustodyEventCreate
from app.services.custody_rules import validate_payload
from app.services.errors import ConflictError, DuplicateError, ForbiddenError, NotFoundError
from app.services.locks import lock_ids

# Re-export the original exception names for existing route/admin imports.
__all__ = ["DuplicateError", "NotFoundError", "apply_batch_created", "apply_custody_event", "existing_ids"]

_STATUS_TRANSITIONS = {
    CustodyEventType.DRYING_STARTED: BatchStatus.DRYING,
    CustodyEventType.DRYING_COMPLETED: BatchStatus.DRIED,
    CustodyEventType.TRANSFERRED_TO_SUPPLIER: BatchStatus.WITH_SUPPLIER,
    CustodyEventType.TRANSFERRED_TO_BUYER: BatchStatus.WITH_BUYER,
    CustodyEventType.EXPORTED: BatchStatus.EXPORTED,
    CustodyEventType.REJECTED: BatchStatus.REJECTED,
}
_DRYING_EVENTS = {CustodyEventType.DRYING_STARTED, CustodyEventType.DRYING_COMPLETED}
_TRANSFER_EVENTS = {CustodyEventType.TRANSFERRED_TO_SUPPLIER, CustodyEventType.TRANSFERRED_TO_BUYER}


def creation_payload(item: BatchCreate) -> dict:
    return {
        "species": item.species, "estimated_weight_kg": str(item.estimated_weight_kg), "unit": item.unit,
        "harvest_latitude": str(item.harvest_latitude) if item.harvest_latitude is not None else None,
        "harvest_longitude": str(item.harvest_longitude) if item.harvest_longitude is not None else None,
    }


def _same_creation(left: dict, right: dict) -> bool:
    for key in ("estimated_weight_kg", "harvest_latitude", "harvest_longitude"):
        a, b = left.get(key), right.get(key)
        if (a is None) != (b is None) or (a is not None and Decimal(str(a)) != Decimal(str(b))):
            return False
    return all(left.get(key) == right.get(key) for key in ("species", "unit"))


async def apply_batch_created(db: AsyncSession, item: BatchCreate, farmer: User) -> HarvestBatch:
    if farmer.role != UserRole.FARMER:
        raise ForbiddenError("Only a farmer can log a harvest")
    await lock_ids(db, "batch", [item.id])
    await lock_ids(db, "event", [item.id])
    existing = await db.get(ChainOfCustodyEvent, item.id)
    batch = await db.get(HarvestBatch, item.id)
    payload = creation_payload(item)
    if batch is not None or existing is not None:
        if (batch is not None and existing is not None and existing.actor_id == farmer.id
                and existing.batch_id == item.id and existing.event_type == CustodyEventType.BATCH_CREATED
                and _same_creation(existing.payload, payload) and as_utc(existing.occurred_at) == as_utc(item.harvested_at)):
            raise DuplicateError("Harvest already applied")
        raise ConflictError("This id is already used for a different record")
    batch = HarvestBatch(
        id=item.id, farmer_id=farmer.id, species=item.species, estimated_weight_kg=item.estimated_weight_kg,
        unit=item.unit, harvest_latitude=item.harvest_latitude, harvest_longitude=item.harvest_longitude,
        harvested_at=item.harvested_at, status=BatchStatus.HARVESTED, current_holder_id=farmer.id, version=1,
    )
    db.add(batch)
    # Flush the parent explicitly: production sessions have autoflush=False
    # and the event table has a real PostgreSQL foreign key to this row.
    await db.flush()
    db.add(ChainOfCustodyEvent(id=item.id, batch_id=item.id, event_type=CustodyEventType.BATCH_CREATED,
                             actor_id=farmer.id, actor_role=farmer.role, occurred_at=item.harvested_at, payload=payload))
    await db.flush()
    return batch


async def _authorize(db: AsyncSession, item: CustodyEventCreate, batch: HarvestBatch, actor: User) -> bool:
    """Return True for a delayed farmer drying event that must not regress custody."""
    kind, state = item.event_type, batch.status
    holder = batch.current_holder_id == actor.id
    if kind == CustodyEventType.BATCH_CREATED:
        raise ConflictError("Create harvests through /batches or a batch_created sync item")
    if as_utc(item.occurred_at) < as_utc(batch.harvested_at):
        raise ConflictError("An event cannot occur before the harvest")
    if kind in _DRYING_EVENTS:
        if actor.role != UserRole.FARMER or actor.id != batch.farmer_id:
            raise ForbiddenError("Only the originating farmer can record drying")
        if not holder:
            first_transfer = await db.scalar(select(ChainOfCustodyEvent.occurred_at).where(
                ChainOfCustodyEvent.batch_id == batch.id,
                ChainOfCustodyEvent.event_type.in_(_TRANSFER_EVENTS),
            ).order_by(ChainOfCustodyEvent.occurred_at).limit(1))
            if first_transfer is not None and as_utc(item.occurred_at) <= as_utc(first_transfer):
                return True
            raise ForbiddenError("The batch is no longer in the farmer's custody")
        expected = BatchStatus.HARVESTED if kind == CustodyEventType.DRYING_STARTED else BatchStatus.DRYING
        if state != expected:
            raise ConflictError(f"Cannot record {kind.value} while batch is {state.value}")
    elif kind in _TRANSFER_EVENTS:
        role, expected = ((UserRole.SUPPLIER, BatchStatus.DRIED) if kind == CustodyEventType.TRANSFERRED_TO_SUPPLIER
                          else (UserRole.BUYER, BatchStatus.WITH_SUPPLIER))
        if actor.role != role:
            raise ForbiddenError(f"This receipt must be confirmed by a {role.value}")
        if state != expected:
            raise ConflictError(f"Batch is not available for this transfer ({state.value})")
    elif kind == CustodyEventType.QUALITY_GRADED:
        receiving = ((actor.role == UserRole.SUPPLIER and state == BatchStatus.DRIED)
                     or (actor.role == UserRole.BUYER and state == BatchStatus.WITH_SUPPLIER))
        if actor.role == UserRole.FARMER or not (holder or receiving):
            raise ForbiddenError("Only the holder or eligible receiving trader can grade this batch")
    elif kind == CustodyEventType.EXPORTED:
        if actor.role != UserRole.BUYER or not holder:
            raise ForbiddenError("Only the buyer holding this batch can record export")
        if state != BatchStatus.WITH_BUYER:
            raise ConflictError("Only a purchased batch can be exported")
    elif kind == CustodyEventType.REJECTED:
        if not holder:
            raise ForbiddenError("Only the current holder can reject a batch")
        if state in {BatchStatus.EXPORTED, BatchStatus.REJECTED}:
            raise ConflictError("This batch is already finalized")
    else:
        participant = actor.id == batch.farmer_id or holder or await db.scalar(select(ChainOfCustodyEvent.id).where(
            ChainOfCustodyEvent.batch_id == batch.id, ChainOfCustodyEvent.actor_id == actor.id).limit(1)) is not None
        if not participant:
            raise ForbiddenError("Only a participant in this batch can add this record")
        if kind in {CustodyEventType.PRICE_AGREED, CustodyEventType.PAYMENT_RECORDED} and actor.role == UserRole.FARMER:
            raise ForbiddenError("Trading records must be posted by a supplier or buyer")
    if kind in _STATUS_TRANSITIONS:
        latest = await db.scalar(select(ChainOfCustodyEvent.occurred_at).where(
            ChainOfCustodyEvent.batch_id == batch.id, ChainOfCustodyEvent.event_type.in_(_STATUS_TRANSITIONS),
        ).order_by(ChainOfCustodyEvent.occurred_at.desc()).limit(1))
        if latest is not None and as_utc(item.occurred_at) < as_utc(latest):
            raise ConflictError("A custody change cannot precede the previous status change")
    return False


async def apply_custody_event(db: AsyncSession, item: CustodyEventCreate, actor: User) -> ChainOfCustodyEvent:
    await lock_ids(db, "batch", [item.batch_id])
    await lock_ids(db, "event", [item.id])
    existing = await db.get(ChainOfCustodyEvent, item.id)
    if existing is not None:
        # Online handover retries retain their UUID but can regenerate the
        # device timestamp. First-write time wins; actor and intent must match.
        if (existing.actor_id == actor.id and existing.batch_id == item.batch_id
                and existing.event_type == item.event_type and existing.payload == item.payload):
            raise DuplicateError("Custody event already applied")
        raise ConflictError("This id is already used for a different record")
    batch = await db.scalar(select(HarvestBatch).where(HarvestBatch.id == item.batch_id)
                            .with_for_update().execution_options(populate_existing=True))
    if batch is None:
        raise NotFoundError(f"batch {item.batch_id} not found")
    historical = await _authorize(db, item, batch, actor)
    await validate_payload(db, item, actor)
    event = ChainOfCustodyEvent(id=item.id, batch_id=item.batch_id, event_type=item.event_type,
                               actor_id=actor.id, actor_role=actor.role, occurred_at=item.occurred_at, payload=item.payload)
    db.add(event)
    if not historical:
        if item.event_type in _STATUS_TRANSITIONS:
            batch.status = _STATUS_TRANSITIONS[item.event_type]
        if item.event_type in _TRANSFER_EVENTS:
            batch.current_holder_id = actor.id
    batch.version += 1
    await db.flush()
    return event


async def existing_ids(db: AsyncSession, model: type, ids: list[uuid.UUID]) -> set[uuid.UUID]:
    if not ids:
        return set()
    return set((await db.scalars(select(model.id).where(model.id.in_(ids)))).all())
