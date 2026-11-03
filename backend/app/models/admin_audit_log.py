import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditAction(str, enum.Enum):
    LOGIN = "login"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    STATUS_CHANGE = "status_change"
    RETRY_ANCHOR = "retry_anchor"
    PRINT = "print"


class AdminAuditLog(Base):
    """Append-only record of what the Super Admin did.

    The admin is not a `users` row (credentials live in the environment), so
    the actor is stored as an identifier string rather than a foreign key.
    `summary` may name records and the *names* of changed fields, but it must
    never contain field values, passwords, tokens or any other secret. Nothing
    in the app updates or deletes these rows.
    """

    __tablename__ = "admin_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    admin_email: Mapped[str] = mapped_column(String(320), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    resource: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    record_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
