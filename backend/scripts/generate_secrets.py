"""Create local deployment secrets without printing their values.

Run from backend: python scripts/generate_secrets.py
Existing non-placeholder values are preserved unless --rotate is supplied.
"""
import argparse
import os
from pathlib import Path
import re
import secrets
import tempfile

from dotenv import dotenv_values

PLACEHOLDERS = {"", "change-me-to-a-random-secret", "change-this-cron-secret"}


def prepare(env_file: Path, *, rotate: bool = False) -> list[str]:
    text = env_file.read_text(encoding="utf-8-sig") if env_file.exists() else ""
    values = dotenv_values(env_file) if env_file.exists() else {}
    changed = []
    for key in ("SECRET_KEY", "CRON_SECRET"):
        current = values.get(key) or ""
        if not rotate and current not in PLACEHOLDERS and len(current) >= 32:
            continue
        value = secrets.token_urlsafe(48)
        pattern = rf"^(?:export\s+)?{key}\s*=.*$"
        replacement = f"{key}={value}"
        if re.search(pattern, text, flags=re.MULTILINE):
            text = re.sub(pattern, lambda _: replacement, text, flags=re.MULTILINE)
        else:
            text = text.rstrip("\r\n") + ("\n" if text else "") + replacement + "\n"
        changed.append(key)
    if changed:
        fd, temporary = tempfile.mkstemp(prefix=".env.", suffix=".tmp", dir=env_file.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output:
                output.write(text)
            os.replace(temporary, env_file)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rotate", action="store_true", help="Replace existing secrets too (invalidates existing JWTs)")
    args = parser.parse_args()
    env_file = Path(__file__).resolve().parents[1] / ".env"
    changed = prepare(env_file, rotate=args.rotate)
    print(f"Updated {', '.join(changed)} in backend/.env (values hidden)." if changed else "Existing secrets are already configured; nothing changed.")


if __name__ == "__main__":
    main()
