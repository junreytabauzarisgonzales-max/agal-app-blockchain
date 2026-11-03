import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.admin import ui
from app.admin.auth import AdminAuthRequired, CSRFError
from app.admin.router import router
from app.admin.views import router as views_router
from app.core.config import settings

logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent / "static"

_ADMIN_CSP = "default-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; object-src 'none'"


def is_admin_path(path: str) -> bool:
    return path == "/admin" or path.startswith("/admin/")


def apply_admin_headers(response: Response) -> Response:
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = _ADMIN_CSP
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


class NoAdminCORSMiddleware(CORSMiddleware):
    """The API's CORS policy (`*` origins with credentials) exists for the mobile/web
    clients. It must never apply to /admin: that would let any other origin that
    can send the admin's cookie (a sibling subdomain, another local port) also
    READ admin responses. Admin requests skip CORS handling entirely, so they get
    no Access-Control-* headers and preflights are refused."""

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] in ("http", "websocket") and is_admin_path(scope.get("path", "")):
            await self.app(scope, receive, send)
            return
        await super().__call__(scope, receive, send)


def _error_page(request: Request, status_code: int, title: str, message: str) -> Response:
    """Standalone (no session needed) HTML error page. Never includes request input
    or exception details."""
    response = ui.templates.TemplateResponse(
        request,
        "admin_error.html",
        {"app_name": settings.PROJECT_NAME, "title": title, "message": message, "status_code": status_code},
        status_code=status_code,
    )
    return apply_admin_headers(response)


def setup_admin(app: FastAPI) -> None:
    """Mounts the Super Admin UI under /admin/*. Its routes are kept out of the
    OpenAPI schema, so nothing about the admin shows up in /docs or /redoc."""

    @app.exception_handler(AdminAuthRequired)
    async def _auth_required(request: Request, exc: AdminAuthRequired) -> RedirectResponse:
        return RedirectResponse("/admin/login", status_code=303)

    @app.exception_handler(CSRFError)
    async def _csrf_failed(request: Request, exc: CSRFError) -> Response:
        return _error_page(
            request, 403, "Request blocked", "This request could not be verified. Reload the page and try again."
        )

    # Errors under /admin become plain HTML pages. Everything else keeps the API's
    # existing JSON behaviour, so the mobile clients see no change.
    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException) -> Response:
        if not is_admin_path(request.url.path):
            return await http_exception_handler(request, exc)
        messages = {404: "That page does not exist.", 405: "That action is not allowed here."}
        return _error_page(
            request, exc.status_code, "Something went wrong",
            messages.get(exc.status_code, "The request could not be completed."),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError) -> Response:
        if not is_admin_path(request.url.path):
            return await request_validation_exception_handler(request, exc)
        # The default handler echoes submitted values back (e.g. an oversized password).
        return _error_page(request, 422, "Invalid request", "Some of the submitted values were not valid.")

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> Response:
        logger.exception("unhandled error on %s %s", request.method, request.url.path)
        if not is_admin_path(request.url.path):
            return PlainTextResponse("Internal Server Error", status_code=500)
        return _error_page(
            request, 500, "Something went wrong", "An unexpected error occurred. It has been logged; please try again."
        )

    @app.middleware("http")
    async def _admin_security_headers(request: Request, call_next):
        response = await call_next(request)
        if is_admin_path(request.url.path):
            apply_admin_headers(response)
        return response

    app.mount("/admin/static", StaticFiles(directory=_STATIC_DIR), name="admin-static")
    app.include_router(router)
    app.include_router(views_router)


__all__ = ["NoAdminCORSMiddleware", "setup_admin"]
