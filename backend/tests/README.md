# Backend tests

The suite covers the Super Admin UI (`app/admin/`) and pins the behaviour of the
existing API around it. It needs **no external services**: each test gets a throwaway
SQLite database (via a `get_db` override in `conftest.py`, with `JSONB` mapped to
`JSON`), a fake blockchain, and fixed admin settings. It never touches the real
(Neon) database or your `backend/.env` admin credentials.

## Run

```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest                                                # all tests
pytest tests/test_admin_security.py                   # one file
pytest --cov=app.admin --cov=app.models.admin_audit_log \
       --cov=app.services.chain_anchor --cov=app.core.config --cov-report=term-missing
```

Coverage is configured in `.coveragerc` (`concurrency = greenlet,thread` is required:
without it, code after an `await db...` is wrongly reported as never run).

## What is tested where (brief section 14)

| Requirement | Tests |
|---|---|
| **Authentication**: correct login, invalid login, protected routes, logout, session expiry | `test_admin_auth.py` |
| **Authorization**: normal users cannot reach the admin | `test_api_regression.py` (real registered users, every role; admin cookie does not authenticate the API), `test_admin_auth.py` |
| **Data management**: list, view, create, update, delete | `test_admin_resources.py` |
| **Search, filtering, sorting, pagination** | `test_admin_listing.py` |
| **Dashboard** | `test_admin_dashboard.py` |
| **Printing**: single record, search/filtered results, page, selection, auth, sensitive fields excluded | `test_admin_print.py` |
| **Security**: CSRF on every POST, same-origin checks, CORS isolation, headers, error pages, secrets never rendered, brute-force limits | `test_admin_security.py` |
| **Audit log**: what is logged, what must never be logged, integrity, read-only page, migration | `test_admin_audit.py` |
| **No hardcoded credentials, `.env` ignored, `.env.example` placeholders** (brief section 15) | `test_repo_hygiene.py` |
| **Edge cases**: DB conflicts, missing records, nested redaction, admin disabled | `test_admin_edge_cases.py` |
| **Existing API unchanged** (register/login/profile/prices/retry-anchor) and on-chain anchoring | `test_api_regression.py` |
| **Layout / navigation** | `test_admin_layout.py` |

## Conventions

* Seed data with the sync session from the `db_session_factory` fixture; drive the app
  with `admin_client` (already signed in) or `client` (anonymous).
* State-changing requests go through `post(...)` in `test_admin_resources.py`, which adds
  the CSRF token.
* Tests that protect a rule (redaction, CSRF, credential scans) were checked by
  deliberately breaking the rule and confirming the test fails. Do the same when you add one.

## Known limits

* SQLite stands in for PostgreSQL. Dialect-specific behaviour (case-insensitive `ILIKE`
  plans, UUID-to-text casts, enum ordering, `JSONB`) is not exercised against Postgres.
* Browser behaviour (dialogs, sidebar, row selection, print preview) is not driven by a
  real browser; the JavaScript is syntax-checked with `node --check` and its hooks are
  asserted, but not executed.
* Page numbers in printouts rely on CSS margin boxes (Chromium-based browsers).
