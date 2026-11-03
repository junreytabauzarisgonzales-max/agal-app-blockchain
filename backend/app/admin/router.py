import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin import audit, auth, ui
from app.admin.dashboard import DashboardStats, load_stats
from app.core.config import settings
from app.db.session import get_db
from app.models.admin_audit_log import AuditAction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", include_in_schema=False)


def _login_page(request: Request, *, status_code: int = 200, error: str | None = None) -> Response:
    nonce, token = auth.new_login_csrf()
    response = ui.templates.TemplateResponse(
        request,
        "login.html",
        {"app_name": settings.PROJECT_NAME, "csrf_token": token, "error": error},
        status_code=status_code,
    )
    auth.set_login_csrf_cookie(response, nonce)
    return response


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request) -> Response:
    if not settings.admin_enabled:
        return HTMLResponse("The admin UI is not configured.", status_code=503)
    if await asyncio.to_thread(auth.session_from_request, request) is not None:
        return RedirectResponse("/admin", status_code=303)
    return _login_page(request)


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: Annotated[str, Form(max_length=320)] = "",
    password: Annotated[str, Form(max_length=1024)] = "",
    csrf_token: Annotated[str, Form(max_length=256)] = "",
    db: AsyncSession = Depends(get_db),
) -> Response:
    if not settings.admin_enabled:
        return HTMLResponse("The admin UI is not configured.", status_code=503)
    auth.check_origin(request)

    key = auth.client_key(request)
    if await asyncio.to_thread(auth.login_throttle.is_locked, key):
        return _login_page(request, status_code=429, error="Too many failed attempts. Try again later.")
    if not auth.verify_login_csrf(request, csrf_token):
        return _login_page(request, status_code=403, error="Your form expired. Please try again.")

    if not auth.check_credentials(email, password):
        await asyncio.to_thread(auth.login_throttle.record_failure, key)
        # Never log the submitted email/password -- only who it came from.
        logger.warning("failed admin login from %s", key)
        await audit.record_safely(db, AuditAction.LOGIN_FAILED, request=request, admin_email="unknown",
                                  summary="Invalid credentials")
        return _login_page(request, status_code=401, error="Invalid email or password.")

    await asyncio.to_thread(auth.login_throttle.reset, key)
    # A fresh session id on every login (never reusing one from a prior cookie).
    old = await asyncio.to_thread(auth.session_from_request, request)
    if old is not None:
        await asyncio.to_thread(auth.session_store.destroy, old.sid)
    session = await asyncio.to_thread(auth.session_store.create)
    await audit.record_safely(db, AuditAction.LOGIN, request=request)

    response = RedirectResponse("/admin", status_code=303)
    auth.set_session_cookie(response, session)
    response.delete_cookie(auth.LOGIN_CSRF_COOKIE, path=auth.COOKIE_PATH)
    return response


@router.post("/logout")
async def logout(
    request: Request,
    session: auth.AdminSession = Depends(auth.require_csrf),
    db: AsyncSession = Depends(get_db),
) -> Response:
    await asyncio.to_thread(auth.session_store.destroy, session.sid)
    await audit.record_safely(db, AuditAction.LOGOUT, request=request)
    response = RedirectResponse("/admin/login", status_code=303)
    auth.clear_session_cookie(response)
    return response


@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    session: auth.AdminSession = Depends(auth.require_admin),
    stats: DashboardStats | None = Depends(load_stats),
) -> Response:
    return ui.render(request, "dashboard.html", session, title="Dashboard", active="dashboard", stats=stats)
