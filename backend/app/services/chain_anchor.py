"""Background-task glue that anchors a custody event on HarvestLedger.

Scheduled via FastAPI's BackgroundTasks from the three write paths that
create events (POST /sync, POST /custody-events, POST /batches), so it
runs *after* the API response is already on its way back to the app --
Sepolia confirmation can take several seconds and must never hold up the
Farmer/Supplier/Buyer request. Opens its own DB session since the
request-scoped one is closed by the time this runs.
"""

import asyncio
import logging
from uuid import UUID

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import OnChainStatus
from app.services.chain_hash import compute_event_hash
from app.services.web3_client import record_event_on_chain
from app.services.locks import lock_ids

logger = logging.getLogger(__name__)


async def anchor_event(event_id: UUID) -> None:
    async with AsyncSessionLocal() as db:
        # Coordinate the shared signing wallet across API/worker processes,
        # not just threads. The lock is released on commit or worker failure.
        await lock_ids(db, "chain-wallet", ["harvest-ledger"])
        event = await db.scalar(select(ChainOfCustodyEvent).where(ChainOfCustodyEvent.id == event_id).with_for_update())
        if event is None or event.on_chain_status != OnChainStatus.PENDING:
            return

        data_hash = compute_event_hash(event)
        try:
            result = await asyncio.to_thread(record_event_on_chain, event.id, event.batch_id, data_hash)
        except Exception:
            logger.exception("failed to anchor custody event %s on-chain", event_id)
            event.on_chain_status = OnChainStatus.FAILED
            await db.commit()
            return

        event.on_chain_status = OnChainStatus.ANCHORED
        event.on_chain_tx_hash = result["tx_hash"] or event.on_chain_tx_hash
        event.on_chain_block_number = result["block_number"] or event.on_chain_block_number
        await db.commit()


async def queue_retry(db: AsyncSession, event: ChainOfCustodyEvent) -> bool:
    """Resets a non-anchored event to PENDING so `anchor_event` will pick it up
    (it only ever proceeds for PENDING events). Returns False, changing
    nothing, if the event is already anchored. The caller schedules the task.
    """
    if event.on_chain_status == OnChainStatus.ANCHORED:
        return False
    event.on_chain_status = OnChainStatus.PENDING
    await db.commit()
    return True


async def anchor_pending_events(limit: int = 50, *, retry_failed: bool = False) -> int:
    """Durable recovery path for requests whose background task was interrupted.

    The event table is the outbox: a committed pending row survives process
    restarts and serverless request termination. Safe for repeated cron runs.
    """
    statuses = [OnChainStatus.PENDING]
    if retry_failed:
        statuses.append(OnChainStatus.FAILED)
    async with AsyncSessionLocal() as db:
        ids = list((await db.scalars(select(ChainOfCustodyEvent.id)
            .where(ChainOfCustodyEvent.on_chain_status.in_(statuses))
            .order_by(case((ChainOfCustodyEvent.on_chain_status == OnChainStatus.PENDING, 0), else_=1),
                      ChainOfCustodyEvent.created_at, ChainOfCustodyEvent.id).limit(limit))).all())
    for event_id in ids:
        if retry_failed:
            async with AsyncSessionLocal() as db:
                event = await db.get(ChainOfCustodyEvent, event_id)
                if event is not None and event.on_chain_status == OnChainStatus.FAILED:
                    await queue_retry(db, event)
        await anchor_event(event_id)
    return len(ids)
