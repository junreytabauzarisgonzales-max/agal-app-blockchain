"""Turns list-page URL parameters (search, filters, sort, paging) into SQL.

Every parameter is validated against the resource's allow-lists in
resources.py; unknown or malformed values are silently dropped, so nothing
user-supplied is ever used as a column name or raw SQL. The same object also
describes the active filters and builds links that preserve them -- the print
feature reuses it, so a printout always matches what is on screen.
"""

import math
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import urlencode

from sqlalchemy import Select, or_

from app.admin.resources import Filter, Resource

DEFAULT_PER_PAGE = 25
PER_PAGE_CHOICES = (10, 25, 50, 100)
MAX_SEARCH_LENGTH = 100


@dataclass
class Page:
    number: int
    per_page: int
    total: int

    @property
    def pages(self) -> int:
        return max(1, math.ceil(self.total / self.per_page))

    @property
    def start(self) -> int:
        return 0 if self.total == 0 else (self.number - 1) * self.per_page + 1

    @property
    def end(self) -> int:
        return min(self.number * self.per_page, self.total)

    @property
    def has_prev(self) -> bool:
        return self.number > 1

    @property
    def has_next(self) -> bool:
        return self.number < self.pages

    def clamped(self) -> "Page":
        """Same page, but never past the last one (e.g. after filters shrink the result)."""
        return Page(min(max(self.number, 1), self.pages), self.per_page, self.total)


@dataclass(frozen=True)
class Chip:
    """An applied search/filter, with a link that removes just that one."""

    label: str
    value: str
    remove_qs: str


def _valid_filter_value(f: Filter, raw: str) -> str | None:
    if not raw:
        return None
    if f.kind in ("enum", "choice", "bool", "notnull"):
        return raw if raw in {value for value, _ in f.options} else None
    if f.kind in ("date_from", "date_to"):
        try:
            return date.fromisoformat(raw).isoformat()
        except ValueError:
            return None
    if f.kind == "uuid":
        try:
            return str(uuid.UUID(raw))
        except ValueError:
            return None
    return None


@dataclass
class ListQuery:
    res: Resource
    q: str = ""
    filters: dict[str, str] = field(default_factory=dict)
    sort: str | None = None
    direction: str = "asc"
    page: int = 1
    per_page: int = DEFAULT_PER_PAGE

    # --- SQL ------------------------------------------------------------------

    def conditions(self) -> list:
        model = self.res.model
        conds = []
        if self.q and self.res.search is not None:
            conds.append(self.res.search(self.q))
        for f in self.res.filters:
            value = self.filters.get(f.name)
            if value is None:
                continue
            col = getattr(model, f.columns[0])
            if f.kind == "enum":
                assert f.enum_cls is not None
                conds.append(col == f.enum_cls(value))
            elif f.kind == "choice":
                conds.append(col == value)
            elif f.kind == "bool":
                conds.append(col.is_(value == "1"))
            elif f.kind == "notnull":
                conds.append(col.is_not(None) if value == "yes" else col.is_(None))
            elif f.kind == "uuid":
                target = uuid.UUID(value)
                conds.append(or_(*[getattr(model, name) == target for name in f.columns]))
            else:  # date_from / date_to
                conds.append(self._date_condition(f, col, date.fromisoformat(value)))
        return conds

    def _date_condition(self, f: Filter, col, day: date):
        column_kind = self.res.column(f.columns[0])
        is_plain_date = column_kind is not None and column_kind.kind == "date"
        if is_plain_date:
            return col >= day if f.kind == "date_from" else col <= day
        # Datetime columns: a "to" day is inclusive, so compare against the start of the next day (UTC).
        if f.kind == "date_from":
            return col >= datetime.combine(day, time.min, tzinfo=timezone.utc)
        return col < datetime.combine(day + timedelta(days=1), time.min, tzinfo=timezone.utc)

    def where(self, stmt: Select) -> Select:
        conds = self.conditions()
        return stmt.where(*conds) if conds else stmt

    def ordered(self, stmt: Select) -> Select:
        if self.sort is None:
            return stmt.order_by(*self.res.order_by)
        col = getattr(self.res.model, self.sort)
        clause = col.desc().nulls_last() if self.direction == "desc" else col.asc().nulls_last()
        return stmt.order_by(clause, self.res.model.id)  # id keeps paging stable across ties

    def paged(self, stmt: Select, page: Page) -> Select:
        return stmt.offset((page.number - 1) * page.per_page).limit(page.per_page)

    # --- description & links ----------------------------------------------------

    @property
    def is_filtered(self) -> bool:
        return bool(self.q or self.filters)

    def _params(self) -> dict[str, str]:
        params: dict[str, str] = {}
        if self.q:
            params["q"] = self.q
        params.update(self.filters)
        if self.sort:
            params["sort"] = self.sort
            params["dir"] = self.direction
        if self.per_page != DEFAULT_PER_PAGE:
            params["per_page"] = str(self.per_page)
        if self.page > 1:
            params["page"] = str(self.page)
        return params

    def qs(self, **changes: str | int | None) -> str:
        """Query string for this list with `changes` applied (None removes a key).
        Changing anything except the page returns to page 1."""
        params = self._params()
        for key, value in changes.items():
            key = key.rstrip("_")  # allows qs(from_=...) for reserved words
            if value is None or value == "":
                params.pop(key, None)
            else:
                params[key] = str(value)
        if "page" not in changes:
            params.pop("page", None)
        return f"?{urlencode(params)}" if params else ""

    def qs_clear(self) -> str:
        """Drops the search and every filter but keeps sort and page size."""
        return self.qs(q=None, **{name: None for name in self.filters})

    def sort_qs(self, column: str, default_direction: str = "asc") -> str:
        """Link for a column header: toggles direction if already sorted by it."""
        if self.sort == column:
            return self.qs(sort=column, dir="desc" if self.direction == "asc" else "asc")
        return self.qs(sort=column, dir=default_direction)

    def chips(self) -> list[Chip]:
        chips = []
        if self.q:
            chips.append(Chip("Search", f"“{self.q}”", self.qs(q=None)))
        for f in self.res.filters:
            value = self.filters.get(f.name)
            if value is None:
                continue
            if f.options:
                shown = dict(f.options).get(value, value)
            elif f.kind == "uuid":
                shown = value[:8]
            else:
                shown = value
            chips.append(Chip(f.label, shown, self.qs(**{f.name: None})))
        return chips


def parse(res: Resource, params: Mapping[str, str]) -> ListQuery:
    q = (params.get("q") or "").strip()[:MAX_SEARCH_LENGTH]

    filters: dict[str, str] = {}
    for f in res.filters:
        value = _valid_filter_value(f, (params.get(f.name) or "").strip())
        if value is not None:
            filters[f.name] = value

    sortable = {c.name for c in res.list_columns if c.sortable}
    sort = params.get("sort") if params.get("sort") in sortable else None
    direction = "desc" if params.get("dir") == "desc" else "asc"

    page_raw = params.get("page") or ""
    per_page_raw = params.get("per_page") or ""
    per_page = int(per_page_raw) if per_page_raw.isdigit() and int(per_page_raw) in PER_PAGE_CHOICES else DEFAULT_PER_PAGE
    return ListQuery(
        res=res,
        q=q,
        filters=filters,
        sort=sort,
        direction=direction,
        page=int(page_raw) if page_raw.isdigit() and int(page_raw) > 0 else 1,
        per_page=per_page,
    )
