from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.sync import BatchCreatedSyncItem, MessageSyncItem, SyncItemResult, SyncRequest, SyncResponse
from app.services.chain_anchor import anchor_event
from app.services.messaging import apply_send_message
from app.services.projection import DuplicateError, apply_batch_created, apply_custody_event
from app.services.errors import DomainError
from app.services.locks import lock_ids

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("", response_model=SyncResponse)
async def sync(
    payload: SyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    farmer: User = Depends(require_role(UserRole.FARMER)),
) -> SyncResponse:
    """Idempotent bulk-apply endpoint for the Farmer app's offline queue.

    Each item carries a client-generated id, so replaying the same batch
    (e.g. after a dropped response) is safe: already-applied items come
    back as "duplicate" rather than being re-applied or erroring. Items are
    applied in the order submitted -- within one request that lets a
    "batch_created" item be immediately followed by custody events on that
    same batch. Each item gets its own savepoint so one bad item doesn't
    roll back the rest of the batch.
    """
    results: list[SyncItemResult] = []
    chain_event_ids: list[UUID] = []

    # Acquire shared resources in a consistent order across bulk requests.
    # Direct writes use the same locks. This also makes concurrent UUID retries
    # safe without relying on a check-then-insert race at the primary key.
    events = [item for item in payload.items if not isinstance(item, MessageSyncItem)]
    await lock_ids(db, "batch", [item.id if isinstance(item, BatchCreatedSyncItem) else item.batch_id for item in events])
    await lock_ids(db, "event", [item.id for item in events])
    await lock_ids(db, "message", [item.id for item in payload.items if isinstance(item, MessageSyncItem)])

    for item in payload.items:
        try:
            async with db.begin_nested():
                if isinstance(item, BatchCreatedSyncItem):
                    await apply_batch_created(db, item, farmer)
                    chain_event_ids.append(item.id)
                elif isinstance(item, MessageSyncItem):
                    await apply_send_message(db, item, farmer)
                else:
                    await apply_custody_event(db, item, farmer)
                    chain_event_ids.append(item.id)
        except DuplicateError:
            results.append(SyncItemResult(id=str(item.id), type=item.type, status="duplicate"))
            continue
        except DomainError as exc:
            results.append(SyncItemResult(id=str(item.id), type=item.type, status="error", detail=str(exc)))
            continue

        results.append(SyncItemResult(id=str(item.id), type=item.type, status="created"))

    await db.commit()

    for event_id in chain_event_ids:
        background_tasks.add_task(anchor_event, event_id)

    return SyncResponse(results=results)
