import asyncio
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.custody_event import ChainOfCustodyEvent
from app.models.user import User
from app.schemas.custody_event import CustodyEventCreate, CustodyEventRead, CustodyEventVerification
from app.services.chain_anchor import anchor_event, queue_retry
from app.services.chain_hash import compute_event_hash, uuid_to_bytes32
from app.services.projection import DuplicateError, NotFoundError, apply_custody_event
from app.services.web3_client import get_record, to_hex0x

router = APIRouter(prefix="/custody-events", tags=["custody-events"])


@router.post("", response_model=CustodyEventRead, status_code=status.HTTP_201_CREATED)
async def create_custody_event(
    payload: CustodyEventCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(get_current_user),
) -> ChainOfCustodyEvent:
    """Direct/online path for recording a custody event (e.g. a Supplier
    confirming receipt, a Buyer recording payment). The Farmer app's
    offline-queued events take the same shape through POST /sync.
    """
    try:
        event = await apply_custody_event(db, payload, actor)
    except DuplicateError:
        existing = await db.get(ChainOfCustodyEvent, payload.id)
        assert existing is not None
        return existing
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await db.commit()
    await db.refresh(event)
    background_tasks.add_task(anchor_event, event.id)
    return event


@router.post("/{event_id}/retry-anchor", status_code=status.HTTP_202_ACCEPTED)
async def retry_anchor(
    event_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    """Re-queues anchoring for an event stuck as `failed` (e.g. it was
    first attempted while WEB3_PROVIDER_URL pointed at an unreachable
    node). `anchor_event` only ever proceeds for events whose status is
    exactly PENDING, so a failed event needs to be reset here first --
    without this, a failed anchor has no path to ever being retried.
    """
    event = await db.get(ChainOfCustodyEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custody event not found")
    if not await queue_retry(db, event):
        return {"status": "already anchored"}

    background_tasks.add_task(anchor_event, event_id)
    return {"status": "retry queued"}


@router.get("/{event_id}/verify", response_model=CustodyEventVerification)
async def verify_custody_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> CustodyEventVerification:
    """Independently checks this event against the live contract on
    Sepolia, rather than just returning the backend's own cached
    `on_chain_status`. This is what "Verify on-chain" in the app actually
    calls -- a Supplier or Buyer confirming a batch's history hasn't been
    altered isn't meaningful if it just re-reads the same database that
    recorded the history in the first place.
    """
    event = await db.get(ChainOfCustodyEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custody event not found")

    expected_hash = to_hex0x(compute_event_hash(event))
    expected_batch_id = to_hex0x(uuid_to_bytes32(event.batch_id))

    try:
        record = await asyncio.to_thread(get_record, event_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not reach the blockchain. Try verification again later.") from exc

    on_chain_exists = record["exists"]
    verified = (
        on_chain_exists
        and record["data_hash_hex"] == expected_hash
        and record["batch_id_hex"] == expected_batch_id
    )

    return CustodyEventVerification(
        event_id=event_id,
        on_chain_exists=on_chain_exists,
        verified=verified,
        expected_data_hash=expected_hash,
        on_chain_data_hash=record["data_hash_hex"] if on_chain_exists else None,
        on_chain_recorded_at=(
            datetime.fromtimestamp(record["recorded_at"], tz=timezone.utc) if on_chain_exists else None
        ),
        tx_hash=event.on_chain_tx_hash,
    )
