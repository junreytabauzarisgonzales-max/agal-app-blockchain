"""Registry of the database resources the Super Admin can manage.

Each resource is an explicit allow-list of columns, search fields and filters:
anything not listed here (notably `users.hashed_password`, message bodies) can
never be rendered, searched, sorted, filtered or printed. Only resources that
actually exist in app/models are registered.
"""

import enum
import re
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import String, cast, or_, select
from sqlalchemy.sql.elements import ColumnElement

from app.models.admin_audit_log import AdminAuditLog, AuditAction
from app.models.batch import HarvestBatch
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import BatchStatus, CustodyEventType, OnChainStatus, UserRole
from app.models.message import Message
from app.models.price import PriceRecord
from app.models.user import User

SORTABLE_KINDS = {"text", "enum", "number", "kg", "price", "date", "datetime", "active", "chain", "read"}


@dataclass(frozen=True)
class Column:
    name: str
    label: str
    # text | enum | number | kg | price | date | datetime | active | chain | read
    # | user (FK -> users) | batch (FK -> batches) | id | code
    kind: str = "text"
    primary: bool = False  # the cell that links to the record's detail page
    detail_only: bool = False  # omitted from list tables

    @property
    def sortable(self) -> bool:
        # Ids and foreign keys have no useful order, so they get no sort header.
        return self.kind in SORTABLE_KINDS


@dataclass(frozen=True)
class Filter:
    """One allow-listed list filter. Anything not declared here is never turned into SQL."""

    name: str  # URL parameter
    label: str
    kind: str  # enum | choice | bool | notnull | date_from | date_to | uuid
    columns: tuple[str, ...]  # model attribute(s); several are OR-ed (uuid only)
    options: tuple[tuple[str, str], ...] = ()  # (value, label) for enum/choice/bool/notnull
    enum_cls: type[enum.Enum] | None = None
    hidden: bool = False  # not shown in the filter bar; reachable via links ("View all")


@dataclass(frozen=True)
class Related:
    """Records elsewhere that point at this one."""

    label: str
    resource: str
    fks: tuple[str, ...]  # attribute(s) on the related model referencing this record
    limit: int = 10
    count_only: bool = False  # e.g. messages: show how many, never list them
    filter: str | None = None  # list filter on the target that reproduces this section ("View all")


@dataclass(frozen=True)
class Resource:
    key: str
    label: str
    singular: str
    model: type
    columns: tuple[Column, ...]
    order_by: tuple
    related: tuple[Related, ...] = ()
    search: Callable[[str], ColumnElement] | None = None
    search_hint: str = ""
    filters: tuple[Filter, ...] = ()
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False

    @property
    def base_url(self) -> str:
        return f"/admin/{self.key}"

    @property
    def list_columns(self) -> tuple[Column, ...]:
        return tuple(c for c in self.columns if not c.detail_only)

    @property
    def visible_filters(self) -> tuple[Filter, ...]:
        return tuple(f for f in self.filters if not f.hidden)

    def column(self, name: str) -> Column | None:
        return next((c for c in self.columns if c.name == name), None)


# --- search ---------------------------------------------------------------------
# Each resource lists exactly what a search term may match. Message bodies are
# deliberately absent: searching them would reveal private content.

_LIKE_ESCAPE = "\\"


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _contains(term: str, *columns) -> list[ColumnElement]:
    pattern = f"%{_escape_like(term)}%"
    return [c.ilike(pattern, escape=_LIKE_ESCAPE) for c in columns]


def _id_prefix(term: str, *columns) -> list[ColumnElement]:
    """Ids are matched by prefix (the UI shows the first 8 characters), with or
    without dashes, so it works however the database renders a UUID as text."""
    if not re.fullmatch(r"[0-9a-fA-F-]{2,}", term):
        return []
    clauses = []
    for column in columns:
        as_text = cast(column, String)
        for variant in {term.lower(), term.lower().replace("-", "")}:
            clauses.append(as_text.ilike(f"{_escape_like(variant)}%", escape=_LIKE_ESCAPE))
    return clauses


def _user_ref(term: str, *columns) -> list[ColumnElement]:
    """Matches records whose user reference(s) point at a user with this name/email."""
    matching = select(User.id).where(or_(*_contains(term, User.full_name, User.email)))
    return [c.in_(matching) for c in columns]


def _search_users(term: str) -> ColumnElement:
    return or_(*_contains(term, User.full_name, User.email, User.municipality, User.phone_number))


def _search_prices(term: str) -> ColumnElement:
    return or_(
        *_contains(term, PriceRecord.species, PriceRecord.grade, PriceRecord.municipality, PriceRecord.notes),
        *_user_ref(term, PriceRecord.posted_by_id),
    )


def _search_batches(term: str) -> ColumnElement:
    return or_(
        *_contains(term, HarvestBatch.species),
        *_id_prefix(term, HarvestBatch.id),
        *_user_ref(term, HarvestBatch.farmer_id, HarvestBatch.current_holder_id),
    )


def _search_events(term: str) -> ColumnElement:
    return or_(
        *_contains(term, ChainOfCustodyEvent.on_chain_tx_hash),
        *_id_prefix(term, ChainOfCustodyEvent.id, ChainOfCustodyEvent.batch_id),
        *_user_ref(term, ChainOfCustodyEvent.actor_id),
    )


def _search_messages(term: str) -> ColumnElement:
    return or_(*_id_prefix(term, Message.id), *_user_ref(term, Message.sender_id, Message.recipient_id))


def _search_audit(term: str) -> ColumnElement:
    return or_(
        *_contains(
            term,
            AdminAuditLog.summary,
            AdminAuditLog.admin_email,
            AdminAuditLog.action,
            AdminAuditLog.resource,
            AdminAuditLog.record_id,
            AdminAuditLog.ip_address,
        )
    )


def _options(enum_cls: type[enum.Enum]) -> tuple[tuple[str, str], ...]:
    return tuple((m.value, m.value.replace("_", " ").title()) for m in enum_cls)


# --- resources ------------------------------------------------------------------

USERS = Resource(
    key="users",
    label="Users",
    singular="user",
    model=User,
    columns=(
        Column("full_name", "Name", primary=True),
        Column("email", "Email"),
        Column("role", "Role", "enum"),
        Column("municipality", "Municipality"),
        Column("phone_number", "Phone", detail_only=True),
        Column("is_active", "Status", "active"),
        Column("created_at", "Joined", "datetime"),
        Column("id", "ID", "code", detail_only=True),
    ),
    order_by=(User.created_at.desc(), User.id),
    related=(
        Related("Harvest batches (as farmer)", "batches", ("farmer_id",), filter="farmer"),
        Related("Batches currently held", "batches", ("current_holder_id",), filter="holder"),
        Related("Price records posted", "prices", ("posted_by_id",), filter="poster"),
        Related("Custody events recorded", "events", ("actor_id",), filter="actor"),
        Related("Messages sent or received", "messages", ("sender_id", "recipient_id"), count_only=True, filter="user"),
    ),
    search=_search_users,
    search_hint="Name, email, municipality or phone",
    filters=(
        Filter("role", "Role", "enum", ("role",), _options(UserRole), UserRole),
        Filter("status", "Status", "bool", ("is_active",), (("1", "Active"), ("0", "Inactive"))),
        Filter("from", "Joined from", "date_from", ("created_at",)),
        Filter("to", "Joined to", "date_to", ("created_at",)),
    ),
    can_create=True,
    can_edit=True,
    can_delete=True,
)

PRICES = Resource(
    key="prices",
    label="Price Records",
    singular="price record",
    model=PriceRecord,
    columns=(
        Column("effective_date", "Effective", "date", primary=True),
        Column("species", "Species"),
        Column("grade", "Grade"),
        Column("price_per_kg", "Price / kg", "price"),
        Column("municipality", "Municipality"),
        Column("posted_by_id", "Posted by", "user"),
        Column("created_at", "Created", "datetime"),
        Column("notes", "Notes", detail_only=True),
        Column("id", "ID", "code", detail_only=True),
    ),
    order_by=(PriceRecord.effective_date.desc(), PriceRecord.created_at.desc(), PriceRecord.id),
    search=_search_prices,
    search_hint="Species, grade, municipality, notes or poster",
    filters=(
        Filter("from", "Effective from", "date_from", ("effective_date",)),
        Filter("to", "Effective to", "date_to", ("effective_date",)),
        Filter("poster", "Posted by", "uuid", ("posted_by_id",), hidden=True),
    ),
    can_create=True,
    can_edit=True,
    can_delete=True,
)

# Batches are a projection folded from custody events, so they are read-only.
BATCHES = Resource(
    key="batches",
    label="Harvest Batches",
    singular="harvest batch",
    model=HarvestBatch,
    columns=(
        Column("id", "Batch", "id", primary=True),
        Column("species", "Species"),
        Column("estimated_weight_kg", "Weight", "kg"),
        Column("status", "Status", "enum"),
        Column("farmer_id", "Farmer", "user"),
        Column("current_holder_id", "Held by", "user"),
        Column("harvested_at", "Harvested", "datetime"),
        Column("harvest_latitude", "Latitude", detail_only=True),
        Column("harvest_longitude", "Longitude", detail_only=True),
        Column("unit", "Unit", detail_only=True),
        Column("version", "Version", "number", detail_only=True),
        Column("created_at", "Created", "datetime", detail_only=True),
        Column("updated_at", "Updated", "datetime", detail_only=True),
    ),
    order_by=(HarvestBatch.created_at.desc(), HarvestBatch.id),
    related=(Related("Chain of custody", "events", ("batch_id",), limit=50, filter="batch"),),
    search=_search_batches,
    search_hint="Species, batch id, farmer or holder",
    filters=(
        Filter("status", "Status", "enum", ("status",), _options(BatchStatus), BatchStatus),
        Filter("from", "Harvested from", "date_from", ("harvested_at",)),
        Filter("to", "Harvested to", "date_to", ("harvested_at",)),
        Filter("farmer", "Farmer", "uuid", ("farmer_id",), hidden=True),
        Filter("holder", "Held by", "uuid", ("current_holder_id",), hidden=True),
    ),
)

# Custody events are immutable and hashed on-chain: no create/edit/delete here.
EVENTS = Resource(
    key="events",
    label="Custody Events",
    singular="custody event",
    model=ChainOfCustodyEvent,
    columns=(
        Column("id", "Event", "id", primary=True),
        Column("event_type", "Type", "enum"),
        Column("batch_id", "Batch", "batch"),
        Column("actor_id", "By", "user"),
        Column("actor_role", "Role", "enum"),
        Column("occurred_at", "Occurred", "datetime"),
        Column("on_chain_status", "On-chain", "chain"),
        Column("received_at", "Received", "datetime", detail_only=True),
        Column("on_chain_tx_hash", "Transaction hash", "code", detail_only=True),
        Column("on_chain_block_number", "Block", "number", detail_only=True),
    ),
    order_by=(ChainOfCustodyEvent.received_at.desc(), ChainOfCustodyEvent.id),
    search=_search_events,
    search_hint="Event id, batch id, transaction hash or actor",
    filters=(
        Filter("type", "Type", "enum", ("event_type",), _options(CustodyEventType), CustodyEventType),
        Filter("chain", "On-chain", "enum", ("on_chain_status",), _options(OnChainStatus), OnChainStatus),
        Filter("role", "Actor role", "enum", ("actor_role",), _options(UserRole), UserRole),
        Filter("from", "Occurred from", "date_from", ("occurred_at",)),
        Filter("to", "Occurred to", "date_to", ("occurred_at",)),
        Filter("actor", "Actor", "uuid", ("actor_id",), hidden=True),
        Filter("batch", "Batch", "uuid", ("batch_id",), hidden=True),
    ),
)

# Private conversations: lists show metadata only; a body appears solely on a
# message's own detail page and is never listed, searched or printed in bulk.
MESSAGES = Resource(
    key="messages",
    label="Messages",
    singular="message",
    model=Message,
    columns=(
        Column("id", "Message", "id", primary=True),
        Column("sender_id", "From", "user"),
        Column("recipient_id", "To", "user"),
        Column("occurred_at", "Sent", "datetime"),
        Column("read_at", "Read", "read"),
        Column("received_at", "Received", "datetime", detail_only=True),
    ),
    order_by=(Message.received_at.desc(), Message.id),
    search=_search_messages,
    search_hint="Message id, sender or recipient",
    filters=(
        Filter("state", "Read state", "notnull", ("read_at",), (("yes", "Read"), ("no", "Unread"))),
        Filter("from", "Sent from", "date_from", ("occurred_at",)),
        Filter("to", "Sent to", "date_to", ("occurred_at",)),
        Filter("user", "Participant", "uuid", ("sender_id", "recipient_id"), hidden=True),
    ),
)

# The audit trail is append-only evidence: viewable and printable, never editable or deletable.
AUDIT = Resource(
    key="audit",
    label="Audit Logs",
    singular="audit entry",
    model=AdminAuditLog,
    columns=(
        Column("created_at", "When", "datetime", primary=True),
        Column("admin_email", "Admin"),
        Column("action", "Action", "enum"),
        Column("resource", "Resource"),
        Column("record_id", "Record", "id"),
        Column("summary", "Details"),
        Column("ip_address", "IP address", detail_only=True),
        Column("id", "ID", "code", detail_only=True),
    ),
    order_by=(AdminAuditLog.created_at.desc(), AdminAuditLog.id),
    search=_search_audit,
    search_hint="Details, admin, action, resource, record id or IP",
    filters=(
        Filter("action", "Action", "choice", ("action",), _options(AuditAction)),
        Filter(
            "resource", "Resource", "choice", ("resource",),
            tuple((k, k.replace("_", " ").title()) for k in ("users", "prices", "batches", "events", "messages", "audit")),
        ),
        Filter("from", "From", "date_from", ("created_at",)),
        Filter("to", "To", "date_to", ("created_at",)),
    ),
)

RESOURCES: dict[str, Resource] = {r.key: r for r in (USERS, PRICES, BATCHES, EVENTS, MESSAGES, AUDIT)}

# Keys whose names must never appear in any admin column.
FORBIDDEN_COLUMN_MARKERS = ("password", "secret", "private_key", "token", "api_key")
