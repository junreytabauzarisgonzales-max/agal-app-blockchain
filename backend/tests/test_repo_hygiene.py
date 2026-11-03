"""Section 15 of the brief (environment & Git security) plus repo-wide checks that no
credentials are committed. Nothing here contains a real credential: the values to
look for are read from the developer's own git-ignored backend/.env at test time."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import _ADMIN_PLACEHOLDERS, Settings

BACKEND = Path(__file__).resolve().parent.parent
REPO = BACKEND.parent
MAX_BYTES = 1_000_000
ADMIN_SECRET_KEYS = ("ADMIN_PASSWORD", "ADMIN_SESSION_SECRET")


def _git(*args: str) -> subprocess.CompletedProcess:
    if shutil.which("git") is None:
        pytest.skip("git is not available")
    result = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    if result.returncode == 128:
        pytest.skip("not inside a git repository")
    return result


def repo_files() -> list[Path]:
    """Tracked files plus untracked-but-not-ignored ones: everything a commit could contain."""
    out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=REPO, capture_output=True)
    if out.returncode != 0:
        pytest.skip("cannot list repository files")
    return [REPO / p for p in out.stdout.decode().split("\0") if p]


def read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data:  # binary
        return None
    return data.decode("utf-8", errors="ignore")


def parse_env(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip("\"'")
    return values


def local_admin_credentials() -> list[str]:
    """The developer's real admin credentials from the ignored .env (never placeholders)."""
    env = BACKEND / ".env"
    if not env.exists():
        return []
    values = parse_env(env)
    found = [values.get(k, "") for k in (*ADMIN_SECRET_KEYS, "ADMIN_EMAIL")]
    return [v for v in found if v and v not in _ADMIN_PLACEHOLDERS]


# --- no credentials in anything that could be committed --------------------------------------------------

def test_local_admin_credentials_appear_in_no_committable_file():
    secrets = local_admin_credentials()
    if not secrets:
        pytest.skip("no real admin credentials in backend/.env to check against")
    _git("rev-parse", "--git-dir")
    for path in repo_files():
        text = read_text(path)
        if text is None:
            continue
        for secret in secrets:
            assert secret not in text, f"a local admin credential appears in {path.relative_to(REPO)}"


def test_no_file_assigns_a_real_value_to_the_admin_secrets():
    _git("rev-parse", "--git-dir")
    pattern = re.compile(rf"^[ \t]*({'|'.join(ADMIN_SECRET_KEYS)})[ \t]*=[ \t]*(\S+)", re.MULTILINE)
    offenders = []
    for path in repo_files():
        if "tests" in path.relative_to(REPO).parts or path.suffix in {".pyc"}:
            continue  # test fixtures legitimately define fake values
        text = read_text(path)
        for match in pattern.finditer(text or ""):
            value = match.group(2).strip("\"'")
            if value and value not in _ADMIN_PLACEHOLDERS:
                offenders.append(f"{path.relative_to(REPO)}: {match.group(1)}")
    assert offenders == []


def test_app_source_reads_admin_credentials_only_from_settings():
    for path in (BACKEND / "app" / "admin").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"""(?:ADMIN_PASSWORD|ADMIN_EMAIL|ADMIN_SESSION_SECRET)\s*=\s*["'][^"']+["']""", text), path
    config = (BACKEND / "app" / "core" / "config.py").read_text(encoding="utf-8")
    assert re.search(r"ADMIN_EMAIL: str \| None = None", config)
    assert re.search(r"ADMIN_PASSWORD: str \| None = None", config)     # no default password


# --- git ignores secrets ---------------------------------------------------------------------------------------

@pytest.mark.parametrize("path", ["backend/.env", "backend/.venv/pyvenv.cfg", "backend/app/__pycache__/x.pyc"])
def test_secret_and_generated_files_are_git_ignored(path):
    assert _git("check-ignore", "-q", path).returncode == 0, f"{path} must be ignored"


def test_the_real_env_file_is_not_tracked():
    assert _git("ls-files", "--error-unmatch", "backend/.env").returncode != 0
    assert "backend/.env" not in {p.relative_to(REPO).as_posix() for p in repo_files()}


def test_the_env_example_is_tracked_not_ignored():
    assert _git("check-ignore", "-q", "backend/.env.example").returncode != 0


# --- .env.example ---------------------------------------------------------------------------------------------------

def test_env_example_documents_the_admin_settings_with_placeholders_only():
    values = parse_env(BACKEND / ".env.example")
    assert values["ADMIN_EMAIL"] == "admin@example.com"
    assert values["ADMIN_PASSWORD"] == "change-this-password"
    assert values["ADMIN_SESSION_SECRET"] == "change-this-secret"
    assert {values["ADMIN_EMAIL"], values["ADMIN_PASSWORD"], values["ADMIN_SESSION_SECRET"]} <= _ADMIN_PLACEHOLDERS


def test_copying_env_example_to_production_is_refused():
    values = parse_env(BACKEND / ".env.example")
    admin = {k: v for k, v in values.items() if k.startswith("ADMIN_")}
    Settings(_env_file=None, ENVIRONMENT="development", **admin)  # fine for local development
    with pytest.raises(ValidationError):
        Settings(_env_file=None, ENVIRONMENT="production", **admin)


def test_every_admin_setting_is_documented_in_env_example():
    documented = set(parse_env(BACKEND / ".env.example"))
    assert {"ADMIN_EMAIL", "ADMIN_PASSWORD", "ADMIN_SESSION_SECRET"} <= documented


# --- dependencies -------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["requirements.txt", "requirements-dev.txt"])
def test_dependencies_are_pinned(name):
    for line in (BACKEND / name).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "-r")):
            assert "==" in line, f"{name}: {line} is not pinned"


def test_runtime_requirements_include_what_the_admin_needs():
    text = (BACKEND / "requirements.txt").read_text(encoding="utf-8")
    assert "jinja2==" in text and "itsdangerous==" in text
    dev = (BACKEND / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "pytest==" in dev and "httpx==" in dev and "aiosqlite==" in dev


# --- the admin never embeds API documentation (brief section 12) ------------------------------------------------------------

def test_admin_ui_has_no_api_documentation_anywhere():
    banned = re.compile(r"swagger|redoc|openapi|api[ _-]?explorer|api[ _-]?docs", re.IGNORECASE)
    for base in ("templates", "static"):
        for path in (BACKEND / "app" / "admin" / base).rglob("*"):
            if path.is_file():
                assert not banned.search(path.read_text(encoding="utf-8")), path
    ui_source = (BACKEND / "app" / "admin" / "ui.py").read_text(encoding="utf-8")
    assert not banned.search(ui_source.replace("OpenAPI schema", ""))


def test_existing_api_docs_are_left_unchanged(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert "/admin" not in client.get("/openapi.json").text


# --- integrity of the admin's own files -------------------------------------------------------------------------------------------

def test_admin_files_are_valid_utf8():
    """Catches stray encoding-damaged bytes that would make Python/Jinja refuse a file."""
    for path in (BACKEND / "app" / "admin").rglob("*"):
        if path.is_file() and path.suffix in {".py", ".html", ".css", ".js"}:
            path.read_bytes().decode("utf-8")


def test_every_template_compiles():
    from app.admin import ui

    for path in (BACKEND / "app" / "admin" / "templates").glob("*.html"):
        ui.templates.env.get_template(path.name)


def test_admin_javascript_is_syntactically_valid():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not available")
    result = subprocess.run([node, "--check", str(BACKEND / "app" / "admin" / "static" / "admin.js")], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
