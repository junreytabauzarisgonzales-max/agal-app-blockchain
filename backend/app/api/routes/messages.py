import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageRead, ThreadSummary
from app.services.messaging import apply_send_message, get_thread, list_threads, mark_thread_read
from app.services.projection import DuplicateError, NotFoundError

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    sender: User = Depends(get_current_user),
) -> Message:
    """Direct/online path to send a message. The Farmer app's offline queue
    sends the same shape through POST /sync (type: "message_sent").
    """
    try:
        message = await apply_send_message(db, payload, sender)
    except DuplicateError:
        existing = await db.get(Message, payload.id)
        assert existing is not None
        return existing
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await db.commit()
    await db.refresh(message)
    return message


@router.get("/threads", response_model=list[ThreadSummary])
async def get_threads(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ThreadSummary]:
    return await list_threads(db, user)


@router.get("/with/{counterpart_id}", response_model=list[MessageRead])
async def get_conversation(
    counterpart_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Message]:
    return await get_thread(db, user.id, counterpart_id)


@router.post("/with/{counterpart_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(
    counterpart_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    await mark_thread_read(db, user.id, counterpart_id)
    await db.commit()
