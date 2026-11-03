"""Super Admin authentication.

The admin is NOT a `users` row: credentials come from the environment
(ADMIN_EMAIL / ADMIN_PASSWORD), and a login yields a server-side session whose
random id travels in a signed, HttpOnly cookie. App JWTs are never honored
here, so no farmer/supplier/buyer account can reach /admin.

Sessions and login throttling use shared Upstash Redis when configured,
including on Vercel. Single-process local deployments retain in-memory storage.
"""

import asyncio
import hashlib
import hmac
import logging
import json
import secrets
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from urllib.parse import urlsplit

from fastapi import Depends, Request
from fastapi.responses import Response
from itsdangerous import BadSignature, URLSafeSerializer

from app.core.config import settings
from app.admin import shared_store

logger = logging.getLogger(__name__)

SESSION_COOKIE = "agal_admin_session"
LOGIN_CSRF_COOKIE = "agal_admin_login_csrf"
COOKIE_PATH = "/admin"
LOGIN_CSRF_MAX_AGE_SECONDS = 60 * 60

MAX_FAILED_LOGINS = 5
LOCKOUT_SECONDS = 15 * 60


class AdminAuthRequired(Exception):
    """Raised by `require_admin`; the app-level handler redirects to the login page."""


class CSRFError(Exception):
    pass


@dataclass
class AdminSession:
    sid: str
    created_at: float
    last_seen: float
    # One-shot (level, message) notifications shown on the next page render.
    flashes: list[tuple[str, str]] = field(default_factory=list)


class SessionStore:
    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self._sessions: dict[str, AdminSession] = {}
        self._clock = clock

    def _purge(self, now: float) -> None:
        idle_limit = settings.ADMIN_SESSION_IDLE_MINUTES * 60
        max_limit = settings.ADMIN_SESSION_MAX_MINUTES * 60
        stale = [
            sid for sid, sess in self._sessions.items()
            if now - sess.last_seen > idle_limit or now - sess.created_at > max_limit
        ]
        for sid in stale:
            del self._sessions[sid]

    def create(self) -> AdminSession:
        now = self._clock()
        self._purge(now)  # keeps memory bounded: expired sessions never linger
        session = AdminSession(sid=secrets.token_urlsafe(32), created_at=now, last_seen=now)
        if settings.admin_shared_store_enabled:
            self._save_shared(session, create=True)
        else:
            self._sessions[session.sid] = session
        return session

    def _save_shared(self, session: AdminSession, *, create: bool = False) -> None:
        remaining = min(settings.ADMIN_SESSION_IDLE_MINUTES * 60,
                        session.created_at + settings.ADMIN_SESSION_MAX_MINUTES * 60 - self._clock())
        if remaining <= 0:
            self.destroy(session.sid)
            return
        parts = ["SET", shared_store.key("session", session.sid), json.dumps(asdict(session)), "EX", max(1, int(remaining))]
        if not create:
            parts.append("XX")  # an in-flight request must never resurrect a logged-out session
        shared_store.command(*parts)

    def save(self, session: AdminSession) -> None:
        if settings.admin_shared_store_enabled:
            self._save_shared(session)
        elif session.sid in self._sessions:
            self._sessions[session.sid] = session

    def get(self, sid: str) -> AdminSession | None:
        """Returns the live session and refreshes its idle timer, or None (and
        forgets it) if it has idled out or exceeded its absolute lifetime."""
        if settings.admin_shared_store_enabled:
            raw = shared_store.command("GET", shared_store.key("session", sid))
            if raw is None:
                return None
            try:
                session = AdminSession(**json.loads(raw))
            except (TypeError, ValueError):
                return None
        else:
            session = self._sessions.get(sid)
        if session is None:
            return None
        now = self._clock()
        idle_limit = settings.ADMIN_SESSION_IDLE_MINUTES * 60
        max_limit = settings.ADMIN_SESSION_MAX_MINUTES * 60
        if now - session.last_seen > idle_limit or now - session.created_at > max_limit:
            self.destroy(sid)
            return None
        session.last_seen = now
        if settings.admin_shared_store_enabled:
            self._save_shared(session)
        return session

    def destroy(self, sid: str) -> None:
        if settings.admin_shared_store_enabled:
            shared_store.command("DEL", shared_store.key("session", sid))
        self._sessions.pop(sid, None)

    def clear(self) -> None:
        self._sessions.clear()


class LoginThrottle:
    """Per-client failed-login counter with a temporary lockout."""

    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self._failures: dict[str, tuple[int, float]] = {}
        self._clock = clock

    def is_locked(self, key: str) -> bool:
        if settings.admin_shared_store_enabled:
            count = shared_store.command("GET", self._shared_key(key))
            return int(count or 0) >= MAX_FAILED_LOGINS
        entry = self._failures.get(key)
        if entry is None:
            return False
        count, last = entry
        if self._clock() - last > LOCKOUT_SECONDS:
            del self._failures[key]
            return False
        return count >= MAX_FAILED_LOGINS

    def record_failure(self, key: str) -> None:
        if settings.admin_shared_store_enabled:
            shared_store.command("EVAL", "local n=redis.call('INCR',KEYS[1]); redis.call('EXPIRE',KEYS[1],ARGV[1]); return n",
                                 1, self._shared_key(key), LOCKOUT_SECONDS)
            return
        now = self._clock()
        for stale in [k for k, (_, last) in self._failures.items() if now - last > LOCKOUT_SECONDS]:
            del self._failures[stale]
        count, _ = self._failures.get(key, (0, 0.0))
        self._failures[key] = (count + 1, now)

    def reset(self, key: str) -> None:
        if settings.admin_shared_store_enabled:
            shared_store.command("DEL", self._shared_key(key))
        self._failures.pop(key, None)

    def _shared_key(self, client: str) -> str:
        return shared_store.key("login", hashlib.sha256(client.encode()).hexdigest())

    def clear(self) -> None:
        self._failures.clear()


session_store = SessionStore()
login_throttle = LoginThrottle()


def client_key(request: Request) -> str:
    if settings.VERCEL:
        forwarded = request.headers.get("x-vercel-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _secret() -> str:
    assert settings.ADMIN_SESSION_SECRET
    return settings.ADMIN_SESSION_SECRET


def _digest(value: str) -> bytes:
    # Hashing first gives compare_digest equal-length inputs, so neither the
    # length nor the content of the expected credential leaks through timing.
    return hashlib.sha256(value.encode("utf-8")).digest()


def check_credentials(email: str, password: str) -> bool:
    if not settings.admin_enabled:
        return False
    assert settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD
    email_ok = hmac.compare_digest(_digest(email.strip().lower()), _digest(settings.ADMIN_EMAIL.strip().lower()))
    password_ok = hmac.compare_digest(_digest(password), _digest(settings.ADMIN_PASSWORD))
    return email_ok and password_ok


# --- cookie ---------------------------------------------------------------

def _cookie_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(_secret(), salt="admin-session")


def set_session_cookie(response: Response, session: AdminSession) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        _cookie_serializer().dumps(session.sid),
        max_age=settings.ADMIN_SESSION_MAX_MINUTES * 60,
        path=COOKIE_PATH,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path=COOKIE_PATH)


def session_from_request(request: Request) -> AdminSession | None:
    if not settings.admin_enabled:
        return None
    raw = request.cookies.get(SESSION_COOKIE)
    if not raw:
        return None
    try:
        sid = _cookie_serializer().loads(raw)
    except BadSignature:
        return None
    return session_store.get(sid)


async def require_admin(request: Request) -> AdminSession:
    session = await asyncio.to_thread(session_from_request, request)
    if session is None:
        raise AdminAuthRequired()
    return session


# --- CSRF -----------------------------------------------------------------

def csrf_token_for(session: AdminSession) -> str:
    """Stateless per-session token: an HMAC of the session id under the admin secret."""
    return hmac.new(_secret().encode("utf-8"), f"csrf:{session.sid}".encode(), hashlib.sha256).hexdigest()


def _login_csrf_token(nonce: str) -> str:
    return hmac.new(_secret().encode("utf-8"), f"login-csrf:{nonce}".encode(), hashlib.sha256).hexdigest()


def new_login_csrf() -> tuple[str, str]:
    """Returns (nonce, form_token). The login form has no session yet, so its
    CSRF token is double-submit: the nonce goes in a HttpOnly cookie and the
    form carries an HMAC of it. A cross-site attacker cannot plant the cookie,
    so cannot forge a matching pair."""
    nonce = secrets.token_urlsafe(16)
    return nonce, _login_csrf_token(nonce)


def set_login_csrf_cookie(response: Response, nonce: str) -> None:
    response.set_cookie(
        LOGIN_CSRF_COOKIE,
        nonce,
        max_age=LOGIN_CSRF_MAX_AGE_SECONDS,
        path=COOKIE_PATH,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
    )


def verify_login_csrf(request: Request, token: str) -> bool:
    nonce = request.cookies.get(LOGIN_CSRF_COOKIE)
    if not nonce or not token:
        return False
    return hmac.compare_digest(token.encode("utf-8"), _login_csrf_token(nonce).encode("utf-8"))


def check_origin(request: Request) -> None:
    """Defence in depth on top of the CSRF token and SameSite=Strict cookie.

    Browsers label every request with Sec-Fetch-Site and (for POSTs) Origin; a
    state-changing request must come from this exact origin. `same-site` is not
    good enough -- a sibling subdomain or another local port is same-site but a
    different origin. Non-browser clients send neither header and are allowed.
    """
    site = request.headers.get("sec-fetch-site")
    if site and site not in ("same-origin", "none"):
        raise CSRFError()
    origin = request.headers.get("origin")
    if origin is not None and urlsplit(origin).netloc != request.url.netloc:
        raise CSRFError()


async def require_csrf(request: Request, session: AdminSession = Depends(require_admin)) -> AdminSession:
    """State-changing admin requests must echo the session's CSRF token, either
    as an `X-CSRF-Token` header (fetch/XHR) or a `csrf_token` form field."""
    check_origin(request)
    supplied = request.headers.get("x-csrf-token")
    if not supplied:
        form = await request.form()
        value = form.get("csrf_token")
        supplied = value if isinstance(value, str) else ""
    if not hmac.compare_digest(supplied.encode("utf-8"), csrf_token_for(session).encode("utf-8")):
        raise CSRFError()
    return session
