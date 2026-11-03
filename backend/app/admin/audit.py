"""Audit trail for Super Admin actions.

Two write modes, chosen per action:

* `add()` -- stages the audit row on the caller's session WITHOUT committing, so it
  is committed atomically with the change it describes. If the audit insert fails,
  the change is rolled back too: an admin cannot modify data without a record.
* `record_safely()` -- for login/logout/print, which change no data. A failure is
  logged server-side but never blocks the admin (otherwise a missing audit table
  could lock everyone out of the UI).

Never pass secrets in `summary`: name records and changed *field names*, never values.
"""

import logging
from decimal import Decimal, InvalidOperation

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.admin_audit_log import AdminAuditLog, AuditAction

logger = logging.getLogger(__name__)

MAX_SUMMARY = 500


def client_ip(request: Request | None) -> str | None:
    return request.client.host if request is not None and request.client else None


def _entry(
    action: AuditAction,
    resource: str | None,
    record_id: object | None,
    summary: str | None,
    request: Request | None,
    admin_email: str | None,
) -> AdminAuditLog:
    return AdminAuditLog(
        admin_email=admin_email or settings.ADMIN_EMAIL or "unknown",
        action=action.value,
        resource=resource,
        record_id=str(record_id) if record_id is not None else None,
        summary=summary[:MAX_SUMMARY] if summary else None,
        ip_address=client_ip(request),
    )


def add(
    db: AsyncSession,
    action: AuditAction,
    *,
    resource: str | None = None,
    record_id: object | None = None,
    summary: str | None = None,
    request: Request | None = None,
) -> AdminAuditLog:
    """Stage an audit row; the caller's commit persists it together with the change."""
    entry = _entry(action, resource, record_id, summary, request, None)
    db.add(entry)
    return entry


async def record_safely(
    db: AsyncSession,
    action: AuditAction,
    *,
    resource: str | None = None,
    record_id: object | None = None,
    summary: str | None = None,
    request: Request | None = None,
    admin_email: str | None = None,
) -> None:
    """Write and commit an audit row on its own; never raises."""
    try:
        db.add(_entry(action, resource, record_id, summary, request, admin_email))
        await db.commit()
    except Exception:
        await db.rollback()
        logger.exception("could not write admin audit log (%s)", action.value)


def changed_fields(before: dict, submitted: dict, secret_fields: tuple[str, ...] = ("password",)) -> list[str]:
    """Names (never values) of fields the admin changed. A supplied password counts
    as changed, since the stored value is a hash and cannot be compared."""
    names = []
    for name, value in submitted.items():
        if name in secret_fields:
            if value:
                names.append(name)
        elif not _same(before.get(name), value):
            names.append(name)
    return names


def _same(before: object, submitted: object) -> bool:
    a = str(before if before is not None else "").strip()
    b = str(submitted if submitted is not None else "").strip()
    if a == b:
        return True
    try:  # "33.50" and "33.5" are the same price
        return Decimal(a) == Decimal(b)
    except InvalidOperation:
        return False
