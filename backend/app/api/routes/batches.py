import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.batch import HarvestBatch
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import BatchStatus, UserRole
from app.models.user import User
from app.schemas.batch import BatchCreate, BatchRead
from app.schemas.custody_event import CustodyEventRead
from app.services.chain_anchor import anchor_event
from app.services.projection import DuplicateError, apply_batch_created

router = APIRouter(prefix="/batches", tags=["batches"])


@router.post("", response_model=BatchRead, status_code=status.HTTP_201_CREATED)
async def create_batch(
    payload: BatchCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    farmer: User = Depends(require_role(UserRole.FARMER)),
) -> HarvestBatch:
    """Direct/online path to create a batch. The Farmer app's primary path is
    queueing the same shape through POST /sync; this exists so a batch can
    also be created without going through the offline queue, and is
    idempotent on `id` exactly like /sync is.
    """
    try:
        batch = await apply_batch_created(db, payload, farmer)
    except DuplicateError:
        existing = await db.get(HarvestBatch, payload.id)
        assert existing is not None
        return existing
    await db.commit()
    await db.refresh(batch)
    background_tasks.add_task(anchor_event, batch.id)
    return batch


@router.get("", response_model=list[BatchRead])
async def list_batches(
    farmer_id: uuid.UUID | None = Query(default=None),
    holder_id: uuid.UUID | None = Query(default=None),
    status_filter: BatchStatus | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[HarvestBatch]:
    stmt = select(HarvestBatch).order_by(HarvestBatch.created_at.desc())
    if farmer_id is not None:
        stmt = stmt.where(HarvestBatch.farmer_id == farmer_id)
    if holder_id is not None:
        stmt = stmt.where(HarvestBatch.current_holder_id == holder_id)
    if status_filter is not None:
        stmt = stmt.where(HarvestBatch.status == status_filter)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{batch_id}", response_model=BatchRead)
async def get_batch(
    batch_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> HarvestBatch:
    batch = await db.get(HarvestBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")
    return batch


@router.get("/{batch_id}/events", response_model=list[CustodyEventRead])
async def get_batch_events(
    batch_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ChainOfCustodyEvent]:
    """Full chain-of-custody history for a batch, oldest first -- this is
    the sequence whose per-event hashes are anchored on HarvestLedger.
    """
    batch = await db.get(HarvestBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")
    stmt = (
        select(ChainOfCustodyEvent)
        .where(ChainOfCustodyEvent.batch_id == batch_id)
        .order_by(ChainOfCustodyEvent.occurred_at.asc(), ChainOfCustodyEvent.received_at.asc(), ChainOfCustodyEvent.id.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
