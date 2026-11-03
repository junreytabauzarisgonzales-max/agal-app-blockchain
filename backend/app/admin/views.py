"""Resource management pages: list, detail, create/edit/delete, and the few
resource-specific actions (user activation, custody-event retry/verify)."""

import json
import logging
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin import audit, auth, ui
from app.admin.forms import FORMS
from app.admin.listing import DEFAULT_PER_PAGE, PER_PAGE_CHOICES, Page, parse
from app.admin.resources import RESOURCES, Related, Resource
from app.api.routes.custody_events import verify_custody_event
from app.core.config import settings
from app.db.session import get_db
from app.models.admin_audit_log import AuditAction
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import OnChainStatus
from app.models.user import User
from app.services.chain_anchor import anchor_event, queue_retry

logger = logging.getLogger(__name__)

PER_PAGE = DEFAULT_PER_PAGE
# A printout is rendered in one response, so it is bounded: bigger result sets are cut
# off with a visible notice rather than exhausting memory or the database.
MAX_PRINT_ROWS = 5000
MAX_SELECTED = 100

# Routes here use full /admin/... paths (each resource carries its own base_url).
router = APIRouter(include_in_schema=False)

_SENSITIVE_KEY = re.compile(r"pass(word|wd)|secret|token|private|api[_-]?key|authorization|credential", re.IGNORECASE)


# --- helpers -----------------------------------------------------------------

@dataclass
class RelatedSection:
    rel: Related
    target: Resource
    total: int
    rows: list[Any]

    @property
    def columns(self):
        return tuple(c for c in self.target.list_columns if c.name not in self.rel.fks)


def _parse_id(raw: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(raw)
    except ValueError:
        return None


def _redact(value: Any) -> Any:
    """Payloads are free-form JSON: blank anything that looks like a credential."""
    if isinstance(value, dict):
        return {k: "[redacted]" if _SENSITIVE_KEY.search(str(k)) else _redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v) for v in value]
    return value


def _display_name(res: Resource, obj: Any) -> str:
    if res.key == "users":
        return obj.full_name
    if res.key == "prices":
        return f"{obj.species} - {obj.effective_date.isoformat()}"
    return f"{res.singular.capitalize()} {str(obj.id)[:8]}"


NAME_LOOKUP_CHUNK = 500


async def _user_names(db: AsyncSession, groups: list[tuple[Any, list[Any]]]) -> dict[uuid.UUID, str]:
    """Resolves every user id shown on a page to a name, in IN-queries of bounded size."""
    ids: set[uuid.UUID] = set()
    for columns, rows in groups:
        for col in columns:
            if col.kind == "user":
                ids.update(getattr(r, col.name) for r in rows if getattr(r, col.name) is not None)
    names: dict[uuid.UUID, str] = {}
    id_list = list(ids)
    for i in range(0, len(id_list), NAME_LOOKUP_CHUNK):
        chunk = id_list[i:i + NAME_LOOKUP_CHUNK]
        result = await db.execute(select(User.id, User.full_name).where(User.id.in_(chunk)))
        names.update({uid: name for uid, name in result.all()})
    return names


async def _load_related(db: AsyncSession, res: Resource, obj_id: uuid.UUID) -> list[RelatedSection]:
    sections = []
    for rel in res.related:
        target = RESOURCES[rel.resource]
        cond = or_(*[getattr(target.model, fk) == obj_id for fk in rel.fks])
        total = await db.scalar(select(func.count()).select_from(target.model).where(cond)) or 0
        rows: list[Any] = []
        if total and not rel.count_only:
            stmt = select(target.model).where(cond).order_by(*target.order_by).limit(rel.limit)
            rows = list((await db.execute(stmt)).scalars().all())
        sections.append(RelatedSection(rel, target, total, rows))
    return sections


def _not_found(request: Request, session: auth.AdminSession, res: Resource | None = None) -> Response:
    return ui.render(
        request, "error.html", session, title="Not found", active=res.key if res else "", status_code=404,
        message="That record does not exist or has been deleted.",
        back_url=res.base_url if res else "/admin", back_label=f"Back to {res.label}" if res else "Back to dashboard",
    )


def _redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


async def _record_context(db: AsyncSession, res: Resource, obj: Any) -> dict[str, Any]:
    """Everything a single-record page needs; shared by the detail view and its printout
    so both show exactly the same fields, relations and redactions."""
    sections = await _load_related(db, res, obj.id)
    names = await _user_names(db, [(res.columns, [obj])] + [(s.columns, s.rows) for s in sections])
    ctx: dict[str, Any] = {
        "sections": sections,
        "names": names,
        "related_total": sum(s.total for s in sections),
    }
    if res.key == "events":
        ctx["payload_json"] = json.dumps(_redact(obj.payload), indent=2, default=str, sort_keys=True)
        ctx["can_retry"] = obj.on_chain_status != OnChainStatus.ANCHORED
    elif res.key == "messages":
        # Private conversation: the body appears only on one message's own page/printout.
        ctx["message_body"] = obj.body
    return ctx


def _selected_ids(request: Request) -> list[uuid.UUID] | None:
    """Row ids ticked on a list page, or None when no selection was made at all."""
    raw = request.query_params.getlist("id")
    if not raw:
        return None
    ids: list[uuid.UUID] = []
    for value in raw:
        uid = _parse_id(value)
        if uid is not None and uid not in ids:
            ids.append(uid)
    return ids[:MAX_SELECTED]


def _report_meta(res: Resource, title: str, back_url: str) -> dict[str, Any]:
    return {
        "app_name": settings.PROJECT_NAME,
        "title": title,
        "back_url": back_url,
        "generated_at": datetime.now(timezone.utc),
        "generated_by": settings.ADMIN_EMAIL,
    }


# --- generic pages -------------------------------------------------------------

def _register(res: Resource) -> None:
    spec = FORMS.get(res.key)
    base = res.base_url

    async def list_view(
        request: Request,
        session: auth.AdminSession = Depends(auth.require_admin),
        db: AsyncSession = Depends(get_db),
    ) -> Response:
        lq = parse(res, request.query_params)
        total = await db.scalar(lq.where(select(func.count()).select_from(res.model))) or 0
        pager = Page(lq.page, lq.per_page, total).clamped()
        lq.page = pager.number
        stmt = lq.paged(lq.ordered(lq.where(select(res.model))), pager)
        rows = list((await db.execute(stmt)).scalars().all())
        names = await _user_names(db, [(res.list_columns, rows)])
        return ui.render(request, "list.html", session, title=res.label, active=res.key,
                         res=res, rows=rows, page=pager, names=names, lq=lq, per_page_choices=PER_PAGE_CHOICES)

    async def detail_view(
        request: Request,
        obj_id: str,
        session: auth.AdminSession = Depends(auth.require_admin),
        db: AsyncSession = Depends(get_db),
    ) -> Response:
        uid = _parse_id(obj_id)
        obj = await db.get(res.model, uid) if uid else None
        if obj is None:
            return _not_found(request, session, res)

        ctx = await _record_context(db, res, obj)
        return ui.render(
            request, "detail.html", session, title=_display_name(res, obj), active=res.key,
            res=res, obj=obj, deletable=res.can_delete and ctx["related_total"] == 0, **ctx,
        )

    async def print_record(
        request: Request,
        obj_id: str,
        session: auth.AdminSession = Depends(auth.require_admin),
        db: AsyncSession = Depends(get_db),
    ) -> Response:
        uid = _parse_id(obj_id)
        obj = await db.get(res.model, uid) if uid else None
        if obj is None:
            return _not_found(request, session, res)
        ctx = await _record_context(db, res, obj)
        await audit.record_safely(db, AuditAction.PRINT, resource=res.key, record_id=obj.id, request=request,
                                  summary=f"Printed {res.singular}: {_display_name(res, obj)}")
        return ui.templates.TemplateResponse(request, "print_record.html", {
            **_report_meta(res, _display_name(res, obj), f"{base}/{obj.id}"),
            "res": res, "obj": obj, **ctx,
        })

    async def print_list(
        request: Request,
        session: auth.AdminSession = Depends(auth.require_admin),
        db: AsyncSession = Depends(get_db),
    ) -> Response:
        lq = parse(res, request.query_params)
        selected = _selected_ids(request)
        if selected is not None:
            # Explicit row selection wins over search/filters: print exactly what was ticked.
            cond = res.model.id.in_(selected) if selected else res.model.id.is_(None)
            total = await db.scalar(select(func.count()).select_from(res.model).where(cond)) or 0
            stmt = lq.ordered(select(res.model).where(cond))
            scope = f"Selected records ({total:,})"
            chips = []
            truncated = False
        else:
            total = await db.scalar(lq.where(select(func.count()).select_from(res.model))) or 0
            base_stmt = lq.ordered(lq.where(select(res.model)))
            chips = lq.chips()
            if request.query_params.get("scope") == "page":
                pager = Page(lq.page, lq.per_page, total).clamped()
                stmt = lq.paged(base_stmt, pager)
                scope = f"Page {pager.number} of {pager.pages} ({pager.per_page} per page)"
                truncated = False
            else:
                stmt = base_stmt.limit(MAX_PRINT_ROWS)
                scope = "All matching records" if lq.is_filtered else "All records"
                truncated = total > MAX_PRINT_ROWS
        rows = list((await db.execute(stmt)).scalars().all())
        names = await _user_names(db, [(res.list_columns, rows)])
        back = f"{base}{lq.qs()}" if selected is None else base
        await audit.record_safely(db, AuditAction.PRINT, resource=res.key, request=request,
                                  summary=f"Printed {res.label} report: {len(rows)} of {total} records ({scope})")
        return ui.templates.TemplateResponse(request, "print_list.html", {
            **_report_meta(res, res.label, back),
            "res": res, "rows": rows, "names": names, "total": total, "shown": len(rows),
            "scope": scope, "chips": chips, "truncated": truncated, "max_rows": MAX_PRINT_ROWS,
            "sorted_by": res.column(lq.sort).label if lq.sort else None, "direction": lq.direction,
        })

    router.add_api_route(base, list_view, methods=["GET"], response_class=HTMLResponse)

    if spec is not None:
        _register_forms(res, spec)

    # "/print" must come before "/{obj_id}" so it is not parsed as an id.
    router.add_api_route(f"{base}/print", print_list, methods=["GET"], response_class=HTMLResponse)
    router.add_api_route(f"{base}/{{obj_id}}", detail_view, methods=["GET"], response_class=HTMLResponse)
    router.add_api_route(f"{base}/{{obj_id}}/print", print_record, methods=["GET"], response_class=HTMLResponse)

    if res.can_delete:
        async def delete_view(
            request: Request,
            obj_id: str,
            session: auth.AdminSession = Depends(auth.require_csrf),
            db: AsyncSession = Depends(get_db),
        ) -> Response:
            uid = _parse_id(obj_id)
            obj = await db.get(res.model, uid) if uid else None
            if obj is None:
                return _not_found(request, session, res)
            related_total = sum(s.total for s in await _load_related(db, res, obj.id))
            if related_total:
                ui.flash(
                    session,
                    f"This {res.singular} still has {related_total} related record(s) and cannot be deleted. "
                    "Deactivate it instead.",
                    "error",
                )
                return _redirect(f"{base}/{obj.id}")
            name = _display_name(res, obj)
            obj_pk = obj.id  # read now: a rollback below would expire the object
            try:
                audit.add(db, AuditAction.DELETE, resource=res.key, record_id=obj.id, request=request,
                          summary=f"Deleted {res.singular}: {name}")
                await db.delete(obj)
                await db.commit()
            except IntegrityError:
                await db.rollback()
                ui.flash(session, f"Could not delete {res.singular}: it is still referenced elsewhere.", "error")
                return _redirect(f"{base}/{obj_pk}")
            ui.flash(session, f"Deleted {res.singular} “{name}”.")
            return _redirect(base)

        router.add_api_route(f"{base}/{{obj_id}}/delete", delete_view, methods=["POST"])


def _register_forms(res: Resource, spec: Any) -> None:
    base = res.base_url

    async def _form_page(
        request: Request, session: auth.AdminSession, obj: Any, values: dict, errors: dict, locked: set[str],
        status_code: int = 200,
    ) -> Response:
        title = f"New {res.singular}" if obj is None else f"Edit {_display_name(res, obj)}"
        return ui.render(
            request, "form.html", session, title=title, active=res.key, status_code=status_code,
            res=res, obj=obj, fields=spec.fields(obj), values=values, errors=errors, locked=locked,
            action=f"{base}/new" if obj is None else f"{base}/{obj.id}/edit",
            cancel_url=base if obj is None else f"{base}/{obj.id}",
        )

    async def _raw(request: Request, obj: Any, locked: set[str], initial: dict) -> dict[str, Any]:
        form = await request.form()
        raw: dict[str, Any] = {}
        for f in spec.fields(obj):
            if f.type == "checkbox":
                raw[f.name] = f.name in form
            else:
                value = form.get(f.name)
                raw[f.name] = value if isinstance(value, str) else ""
        for name in locked:  # disabled inputs are not submitted; keep the stored value
            raw[name] = initial[name]
        return raw

    async def _initial(db: AsyncSession, obj: Any) -> dict[str, Any]:
        initial = spec.initial(obj)
        if obj is not None and hasattr(spec, "poster_email"):
            initial["posted_by_email"] = await spec.poster_email(db, obj)
        return initial

    async def _locked(db: AsyncSession, obj: Any) -> set[str]:
        # A user's role decides which records they can own, so it is frozen once they have any.
        if res.key == "users" and obj is not None:
            if sum(s.total for s in await _load_related(db, res, obj.id)):
                return {"role"}
        return set()

    async def new_form(
        request: Request,
        session: auth.AdminSession = Depends(auth.require_admin),
        db: AsyncSession = Depends(get_db),
    ) -> Response:
        return await _form_page(request, session, None, await _initial(db, None), {}, set())

    async def new_submit(
        request: Request,
        session: auth.AdminSession = Depends(auth.require_csrf),
        db: AsyncSession = Depends(get_db),
    ) -> Response:
        raw = await _raw(request, None, set(), {})
        cleaned, errors = await spec.validate(db, raw, None)
        if errors:
            return await _form_page(request, session, None, raw, errors, set(), status_code=422)
        try:
            obj = await spec.create(db, cleaned)
            audit.add(db, AuditAction.CREATE, resource=res.key, record_id=obj.id, request=request,
                      summary=f"Created {res.singular}: {_display_name(res, obj)}")
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return await _form_page(request, session, None, raw, {"_form": "That record already exists."}, set(), 409)
        ui.flash(session, f"Created {res.singular} “{_display_name(res, obj)}”.")
        return _redirect(f"{base}/{obj.id}")

    async def edit_form(
        request: Request,
        obj_id: str,
        session: auth.AdminSession = Depends(auth.require_admin),
        db: AsyncSession = Depends(get_db),
    ) -> Response:
        uid = _parse_id(obj_id)
        obj = await db.get(res.model, uid) if uid else None
        if obj is None:
            return _not_found(request, session, res)
        return await _form_page(request, session, obj, await _initial(db, obj), {}, await _locked(db, obj))

    async def edit_submit(
        request: Request,
        obj_id: str,
        session: auth.AdminSession = Depends(auth.require_csrf),
        db: AsyncSession = Depends(get_db),
    ) -> Response:
        uid = _parse_id(obj_id)
        obj = await db.get(res.model, uid) if uid else None
        if obj is None:
            return _not_found(request, session, res)
        locked = await _locked(db, obj)
        initial = await _initial(db, obj)
        raw = await _raw(request, obj, locked, initial)
        cleaned, errors = await spec.validate(db, raw, obj)
        if errors:
            return await _form_page(request, session, obj, raw, errors, locked, status_code=422)
        changed = audit.changed_fields(initial, raw)  # field NAMES only, never values
        try:
            await spec.update(db, obj, cleaned)
            audit.add(db, AuditAction.UPDATE, resource=res.key, record_id=obj.id, request=request,
                      summary=f"Updated {res.singular}: {_display_name(res, obj)}; fields changed: "
                              f"{', '.join(changed) or 'none'}")
            await db.commit()
        except IntegrityError:
            await db.rollback()
            fresh = await db.get(res.model, uid, populate_existing=True)
            if fresh is None:
                return _not_found(request, session, res)
            return await _form_page(
                request, session, fresh, raw, {"_form": "That change conflicts with an existing record."}, locked, 409
            )
        ui.flash(session, f"Saved changes to {res.singular} “{_display_name(res, obj)}”.")
        return _redirect(f"{base}/{obj.id}")

    # "/new" must be registered before "/{obj_id}" so it is not parsed as an id.
    router.add_api_route(f"{base}/new", new_form, methods=["GET"], response_class=HTMLResponse)
    router.add_api_route(f"{base}/new", new_submit, methods=["POST"], response_class=HTMLResponse)
    router.add_api_route(f"{base}/{{obj_id}}/edit", edit_form, methods=["GET"], response_class=HTMLResponse)
    router.add_api_route(f"{base}/{{obj_id}}/edit", edit_submit, methods=["POST"], response_class=HTMLResponse)


for _res in RESOURCES.values():
    _register(_res)


# --- resource-specific actions ---------------------------------------------------------

@router.post("/admin/users/{obj_id}/toggle-active")
async def toggle_user_active(
    request: Request,
    obj_id: str,
    session: auth.AdminSession = Depends(auth.require_csrf),
    db: AsyncSession = Depends(get_db),
) -> Response:
    res = RESOURCES["users"]
    uid = _parse_id(obj_id)
    user = await db.get(User, uid) if uid else None
    if user is None:
        return _not_found(request, session, res)
    user.is_active = not user.is_active
    audit.add(db, AuditAction.STATUS_CHANGE, resource=res.key, record_id=user.id, request=request,
              summary=f"{'Activated' if user.is_active else 'Deactivated'} user: {user.full_name}")
    await db.commit()
    ui.flash(session, f"{user.full_name} is now {'active' if user.is_active else 'inactive'}.")
    return _redirect(f"{res.base_url}/{user.id}")


@router.post("/admin/events/{obj_id}/retry-anchor")
async def retry_event_anchor(
    request: Request,
    obj_id: str,
    background_tasks: BackgroundTasks,
    session: auth.AdminSession = Depends(auth.require_csrf),
    db: AsyncSession = Depends(get_db),
) -> Response:
    res = RESOURCES["events"]
    uid = _parse_id(obj_id)
    event = await db.get(ChainOfCustodyEvent, uid) if uid else None
    if event is None:
        return _not_found(request, session, res)
    if event.on_chain_status != OnChainStatus.ANCHORED:
        # queue_retry commits, which persists this audit row in the same transaction.
        audit.add(db, AuditAction.RETRY_ANCHOR, resource=res.key, record_id=event.id, request=request,
                  summary=f"Queued re-anchoring of custody event {str(event.id)[:8]}")
    if await queue_retry(db, event):
        background_tasks.add_task(anchor_event, event.id)
        ui.flash(session, "Re-anchoring queued. Refresh in a few seconds to see the result.", "info")
    else:
        ui.flash(session, "This event is already anchored on-chain.", "info")
    return _redirect(f"{res.base_url}/{event.id}")


@router.post("/admin/events/{obj_id}/verify")
async def verify_event(
    request: Request,
    obj_id: str,
    session: auth.AdminSession = Depends(auth.require_csrf),
    db: AsyncSession = Depends(get_db),
) -> Response:
    res = RESOURCES["events"]
    uid = _parse_id(obj_id)
    if uid is None or await db.get(ChainOfCustodyEvent, uid) is None:
        return _not_found(request, session, res)
    try:
        result = await verify_custody_event(uid, db, None)
    except HTTPException as exc:
        # The API's 502 detail embeds the raw provider error, which can carry an
        # RPC URL/API key, so log it server-side and show only a generic message.
        logger.warning("admin verify failed for event %s: %s", uid, exc.status_code)
        ui.flash(session, "Could not reach the blockchain to verify this event. Try again later.", "error")
    else:
        if result.verified:
            ui.flash(session, "Verified: the on-chain hash matches this event.", "success")
        elif not result.on_chain_exists:
            ui.flash(session, "This event was not found on-chain.", "warning")
        else:
            ui.flash(session, "MISMATCH: the on-chain hash differs from this event's data.", "error")
    return _redirect(f"{res.base_url}/{uid}")
