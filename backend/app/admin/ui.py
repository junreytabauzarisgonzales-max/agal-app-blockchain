"""Shared UI plumbing for admin pages: the navigation registry, one-shot
flash notifications, and a render helper that wraps every signed-in page in
the common layout (sidebar, topbar, notifications, confirm dialog)."""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from app.admin import auth
from app.core.config import settings

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

FLASH_LEVELS = {"success", "error", "warning", "info"}


def _fmt_datetime(value: datetime | date | None) -> str:
    if value is None:
        return "\u2014"
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return value.isoformat()


def _fmt_number(value: float | None) -> str:
    return f"{value or 0:,.0f}"


def _label(value: str) -> str:
    return value.replace("_", " ").title()


templates.env.filters["dt"] = _fmt_datetime
templates.env.filters["num"] = _fmt_number
templates.env.filters["label"] = _label


@dataclass(frozen=True)
class NavItem:
    key: str
    label: str
    href: str
    # Pages that don't exist yet are listed but rendered as non-links, so the
    # sidebar never points at a 404. Flip to True when the page ships.
    enabled: bool = False


@dataclass(frozen=True)
class NavSection:
    title: str | None
    items: tuple[NavItem, ...]


# Data-management entries mirror the real tables (see app/models); read-only
# resources are marked when they get their pages.
NAV_SECTIONS: tuple[NavSection, ...] = (
    NavSection(None, (NavItem("dashboard", "Dashboard", "/admin", enabled=True),)),
    NavSection(
        "Data Management",
        (
            NavItem("users", "Users", "/admin/users", enabled=True),
            NavItem("prices", "Price Records", "/admin/prices", enabled=True),
            NavItem("batches", "Harvest Batches", "/admin/batches", enabled=True),
            NavItem("events", "Custody Events", "/admin/events", enabled=True),
            NavItem("messages", "Messages", "/admin/messages", enabled=True),
        ),
    ),
    NavSection("Monitoring", (NavItem("audit", "Audit Logs", "/admin/audit", enabled=True),)),
    NavSection("System", (NavItem("settings", "Settings", "/admin/settings"),)),
)


def flash(session: auth.AdminSession, message: str, level: str = "success") -> None:
    """Queue a notification for the admin's next page render."""
    session.flashes.append((level if level in FLASH_LEVELS else "info", message))
    auth.session_store.save(session)


def render(
    request: Request,
    template: str,
    session: auth.AdminSession,
    *,
    title: str,
    active: str,
    status_code: int = 200,
    **context: Any,
) -> Response:
    """Render a page inside the admin layout. `active` is the NavItem key to highlight."""
    flashes, session.flashes = session.flashes, []
    if flashes:
        auth.session_store.save(session)
    return templates.TemplateResponse(
        request,
        template,
        {
            "app_name": settings.PROJECT_NAME,
            "admin_email": settings.ADMIN_EMAIL,
            "csrf_token": auth.csrf_token_for(session),
            "nav_sections": NAV_SECTIONS,
            "active": active,
            "title": title,
            "flashes": flashes,
            **context,
        },
        status_code=status_code,
    )
