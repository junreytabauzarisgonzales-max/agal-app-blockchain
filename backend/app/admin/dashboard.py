"""Read-only statistics for the admin dashboard.

Deliberately cheap: one grouped aggregate per table (totals are derived from
the groups rather than a separate COUNT), plus two tiny LIMIT queries for the
recent-activity lists. Nothing here loads whole tables.
"""

import enum
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.batch import HarvestBatch
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import BatchStatus, OnChainStatus, UserRole
from app.models.message import Message
from app.models.price import PriceRecord
from app.models.user import User

logger = logging.getLogger(__name__)

RECENT_EVENTS_LIMIT = 10
RECENT_USERS_LIMIT = 5


@dataclass(frozen=True)
class Count:
    key: str  # enum value, e.g. "with_supplier"
    label: str  # human label, e.g. "With Supplier"
    count: int


@dataclass(frozen=True)
class RecentEvent:
    occurred_at: datetime
    event_type: str
    actor_name: str
    actor_role: str
    batch_id: str
    on_chain_status: str


@dataclass(frozen=True)
class RecentUser:
    full_name: str
    role: str
    is_active: bool
    created_at: datetime | None


@dataclass
class DashboardStats:
    generated_at: datetime
    users_total: int = 0
    users_active: int = 0
    users_by_role: list[Count] = field(default_factory=list)
    prices_total: int = 0
    prices_latest: date | None = None
    batches_total: int = 0
    batches_total_kg: float = 0.0
    batches_by_status: list[Count] = field(default_factory=list)
    events_total: int = 0
    events_last_24h: int = 0
    events_by_chain: list[Count] = field(default_factory=list)
    messages_total: int = 0
    messages_unread: int = 0
    recent_events: list[RecentEvent] = field(default_factory=list)
    recent_users: list[RecentUser] = field(default_factory=list)

    @property
    def users_inactive(self) -> int:
        return self.users_total - self.users_active

    @property
    def events_failed(self) -> int:
        return next((c.count for c in self.events_by_chain if c.key == OnChainStatus.FAILED.value), 0)

    @property
    def events_pending(self) -> int:
        return next((c.count for c in self.events_by_chain if c.key == OnChainStatus.PENDING.value), 0)


def label_for(value: enum.Enum | str) -> str:
    raw = value.value if isinstance(value, enum.Enum) else str(value)
    return raw.replace("_", " ").title()


def _value(value: enum.Enum | str) -> str:
    return value.value if isinstance(value, enum.Enum) else str(value)


def _breakdown(enum_cls: type[enum.Enum], counts: dict[str, int]) -> list[Count]:
    """Every enum member in declaration order (zeros included) so panels keep a stable shape."""
    return [Count(m.value, label_for(m), counts.get(m.value, 0)) for m in enum_cls]


async def collect_stats(db: AsyncSession) -> DashboardStats:
    now = datetime.now(timezone.utc)
    stats = DashboardStats(generated_at=now)

    # Users: role x active, one query.
    by_role: dict[str, int] = {}
    for role, is_active, n in (
        await db.execute(select(User.role, User.is_active, func.count()).group_by(User.role, User.is_active))
    ).all():
        by_role[_value(role)] = by_role.get(_value(role), 0) + n
        stats.users_total += n
        if is_active:
            stats.users_active += n
    stats.users_by_role = _breakdown(UserRole, by_role)

    # Price records
    stats.prices_total, stats.prices_latest = (
        await db.execute(select(func.count(), func.max(PriceRecord.effective_date)))
    ).one()

    # Batches: status breakdown + total weight
    by_status: dict[str, int] = {}
    for status, n, kg in (
        await db.execute(
            select(HarvestBatch.status, func.count(), func.coalesce(func.sum(HarvestBatch.estimated_weight_kg), 0))
            .group_by(HarvestBatch.status)
        )
    ).all():
        by_status[_value(status)] = n
        stats.batches_total += n
        stats.batches_total_kg += float(kg)
    stats.batches_by_status = _breakdown(BatchStatus, by_status)

    # Custody events: on-chain status breakdown + last-24h volume
    cutoff = now - timedelta(hours=24)
    by_chain: dict[str, int] = {}
    for chain_status, n, recent in (
        await db.execute(
            select(
                ChainOfCustodyEvent.on_chain_status,
                func.count(),
                func.count().filter(ChainOfCustodyEvent.received_at >= cutoff),
            ).group_by(ChainOfCustodyEvent.on_chain_status)
        )
    ).all():
        by_chain[_value(chain_status)] = n
        stats.events_total += n
        stats.events_last_24h += recent
    stats.events_by_chain = _breakdown(OnChainStatus, by_chain)

    # Messages: counts only -- the dashboard never reads message bodies.
    stats.messages_total, stats.messages_unread = (
        await db.execute(select(func.count(), func.count().filter(Message.read_at.is_(None))))
    ).one()

    # Recent activity
    events = await db.execute(
        select(
            ChainOfCustodyEvent.occurred_at,
            ChainOfCustodyEvent.event_type,
            User.full_name,
            ChainOfCustodyEvent.actor_role,
            ChainOfCustodyEvent.batch_id,
            ChainOfCustodyEvent.on_chain_status,
        )
        .join(User, User.id == ChainOfCustodyEvent.actor_id)
        .order_by(ChainOfCustodyEvent.received_at.desc())
        .limit(RECENT_EVENTS_LIMIT)
    )
    stats.recent_events = [
        RecentEvent(occurred, _value(etype), name, _value(role), str(batch_id), _value(chain))
        for occurred, etype, name, role, batch_id, chain in events.all()
    ]

    users = await db.execute(
        select(User.full_name, User.role, User.is_active, User.created_at)
        .order_by(User.created_at.desc())
        .limit(RECENT_USERS_LIMIT)
    )
    stats.recent_users = [RecentUser(name, _value(role), active, created) for name, role, active, created in users.all()]

    return stats


async def load_stats(db: AsyncSession = Depends(get_db)) -> DashboardStats | None:
    """Dashboard dependency. A database problem must degrade the page to an
    error state, not turn /admin into a 500, so failures are logged and
    surfaced as None."""
    try:
        return await collect_stats(db)
    except Exception:
        logger.exception("could not load admin dashboard statistics")
        return None
