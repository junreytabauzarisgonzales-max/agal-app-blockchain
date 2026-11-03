"""Direct messaging between accounts -- append-only, same idempotency
pattern as custody events: `id` is client-generated, so replaying a send
(via /sync or a retried POST /messages) is a safe no-op.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, ThreadSummary
from app.services.projection import DuplicateError, NotFoundError
from app.services.errors import ConflictError
from app.services.locks import lock_ids


async def apply_send_message(db: AsyncSession, item: MessageCreate, sender: User) -> Message:
    await lock_ids(db, "message", [item.id])
    existing = await db.get(Message, item.id)
    if existing is not None:
        if existing.sender_id == sender.id and existing.recipient_id == item.recipient_id and existing.body == item.body:
            raise DuplicateError("Message already applied")
        raise ConflictError("This id is already used for a different record")

    recipient = await db.get(User, item.recipient_id)
    if recipient is None or not recipient.is_active:
        raise NotFoundError(f"user {item.recipient_id} not found")

    message = Message(
        id=item.id,
        sender_id=sender.id,
        recipient_id=item.recipient_id,
        body=item.body,
        occurred_at=item.occurred_at,
    )
    db.add(message)
    await db.flush()
    return message


async def list_threads(db: AsyncSession, user: User) -> list[ThreadSummary]:
    stmt = (
        select(Message)
        .where(or_(Message.sender_id == user.id, Message.recipient_id == user.id))
        .order_by(Message.occurred_at.desc())
    )
    messages = (await db.execute(stmt)).scalars().all()
    if not messages:
        return []

    latest_by_counterpart: dict[uuid.UUID, Message] = {}
    unread_counts: dict[uuid.UUID, int] = {}
    for msg in messages:
        counterpart_id = msg.recipient_id if msg.sender_id == user.id else msg.sender_id
        latest_by_counterpart.setdefault(counterpart_id, msg)  # first seen = most recent (already sorted)
        if msg.recipient_id == user.id and msg.read_at is None:
            unread_counts[counterpart_id] = unread_counts.get(counterpart_id, 0) + 1

    counterparts = (await db.execute(select(User).where(User.id.in_(latest_by_counterpart.keys())))).scalars().all()
    counterparts_by_id = {u.id: u for u in counterparts}

    summaries = [
        ThreadSummary(
            counterpart_id=counterpart_id,
            counterpart_name=counterpart.full_name,
            counterpart_role=counterpart.role,
            counterpart_phone_number=counterpart.phone_number,
            last_message_body=latest.body,
            last_message_at=latest.occurred_at,
            unread_count=unread_counts.get(counterpart_id, 0),
        )
        for counterpart_id, latest in latest_by_counterpart.items()
        if (counterpart := counterparts_by_id.get(counterpart_id)) is not None
    ]
    summaries.sort(key=lambda s: s.last_message_at, reverse=True)
    return summaries


async def get_thread(db: AsyncSession, user_id: uuid.UUID, counterpart_id: uuid.UUID) -> list[Message]:
    stmt = (
        select(Message)
        .where(
            or_(
                and_(Message.sender_id == user_id, Message.recipient_id == counterpart_id),
                and_(Message.sender_id == counterpart_id, Message.recipient_id == user_id),
            )
        )
        .order_by(Message.occurred_at.asc())
    )
    return list((await db.execute(stmt)).scalars().all())


async def mark_thread_read(db: AsyncSession, user_id: uuid.UUID, counterpart_id: uuid.UUID) -> None:
    stmt = select(Message).where(
        Message.sender_id == counterpart_id,
        Message.recipient_id == user_id,
        Message.read_at.is_(None),
    )
    unread = (await db.execute(stmt)).scalars().all()
    now = datetime.now(timezone.utc)
    for msg in unread:
        msg.read_at = now
