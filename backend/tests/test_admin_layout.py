import re
from pathlib import Path

from app.admin import auth, ui

TEMPLATES = Path(__file__).resolve().parent.parent / "app" / "admin" / "templates"


def _only_session() -> auth.AdminSession:
    (session,) = auth.session_store._sessions.values()
    return session


def test_dashboard_uses_the_shared_layout(admin_client):
    html = admin_client.get("/admin").text
    assert 'id="sidebar"' in html
    assert 'aria-label="Admin navigation"' in html
    assert 'id="main"' in html
    assert "Data Management" in html
    assert '<script src="/admin/static/admin.js" defer>' in html
    assert 'id="confirm-dialog"' in html


def test_nav_lists_the_real_resources(admin_client):
    html = admin_client.get("/admin").text
    for label in ("Users", "Price Records", "Harvest Batches", "Custody Events", "Messages", "Audit Logs", "Settings"):
        assert label in html


def test_dashboard_is_marked_as_current_page(admin_client):
    html = admin_client.get("/admin").text
    assert re.search(r'class="nav-link is-active"\s+href="/admin"\s+aria-current="page"', html)


def test_unavailable_sections_are_not_links(admin_client):
    html = admin_client.get("/admin").text
    for item in ui.NAV_SECTIONS:
        for nav in item.items:
            if not nav.enabled:
                assert f'href="{nav.href}"' not in html
    assert 'aria-disabled="true"' in html


def test_every_enabled_nav_item_resolves(admin_client):
    for section in ui.NAV_SECTIONS:
        for item in section.items:
            if item.enabled:
                assert admin_client.get(item.href).status_code == 200, item.href


def test_nav_has_no_api_documentation_entries():
    labels = " ".join(item.label.lower() + item.href.lower() for s in ui.NAV_SECTIONS for item in s.items)
    for banned in ("swagger", "redoc", "openapi", "api doc", "/docs", "api explorer"):
        assert banned not in labels


def test_sign_out_form_carries_a_working_csrf_token(admin_client):
    html = admin_client.get("/admin").text
    token = re.search(r'action="/admin/logout">\s*<input type="hidden" name="csrf_token" value="([^"]+)"', html).group(1)
    assert token == auth.csrf_token_for(_only_session())
    assert admin_client.post("/admin/logout", data={"csrf_token": token}).status_code == 303


def test_signed_in_admin_email_is_shown(admin_client):
    assert "test-admin@example.test" in admin_client.get("/admin").text


def test_login_page_does_not_use_the_admin_shell(client):
    html = client.get("/admin/login").text
    assert 'id="sidebar"' not in html
    assert "admin.js" not in html


def test_flash_is_shown_once_then_cleared(admin_client):
    ui.flash(_only_session(), "Record saved", "success")
    first = admin_client.get("/admin").text
    assert "Record saved" in first
    assert "toast-success" in first
    assert "Record saved" not in admin_client.get("/admin").text


def test_error_flash_is_an_alert_and_html_is_escaped(admin_client):
    ui.flash(_only_session(), "<script>alert(1)</script>", "error")
    html = admin_client.get("/admin").text
    assert 'role="alert"' in html
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_unknown_flash_level_falls_back_to_info(admin_client):
    ui.flash(_only_session(), "hello", "bogus")
    assert "toast-info" in admin_client.get("/admin").text


def test_static_assets_are_served(client):
    css = client.get("/admin/static/admin.css")
    js = client.get("/admin/static/admin.js")
    assert css.status_code == 200
    assert js.status_code == 200
    assert "javascript" in js.headers["content-type"]
    assert "data-confirm" in js.text  # confirmation-dialog hook for destructive actions
    assert "@media print" in css.text


def test_templates_have_no_inline_script_style_or_handlers():
    """The admin CSP is `default-src 'self'`, which blocks all of these."""
    for path in TEMPLATES.glob("*.html"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"<script(?![^>]*\bsrc=)", text), path
        assert "<style" not in text, path
        assert not re.search(r'\sstyle="', text), path
        assert not re.search(r"\son[a-z]+=", text), path
        assert "javascript:" not in text, path
