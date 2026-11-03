"""Small Upstash REST adapter for admin state shared by Vercel instances."""
import hashlib
import json
from urllib.request import Request, urlopen

from app.core.config import settings


def key(kind: str, identifier: str) -> str:
    namespace = hashlib.sha256((settings.ADMIN_SESSION_SECRET or "").encode()).hexdigest()[:20]
    return f"agal:admin:{namespace}:{kind}:{identifier}"


def command(*parts):
    request = Request(
        (settings.UPSTASH_REDIS_REST_URL or "").rstrip("/"),
        data=json.dumps(parts).encode(), method="POST",
        headers={"Authorization": f"Bearer {settings.UPSTASH_REDIS_REST_TOKEN}", "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            data = json.load(response)
        if "error" in data:
            raise RuntimeError("Redis command failed")
        return data.get("result")
    except Exception:
        # Do not reflect Redis credentials or provider responses into logs/UI.
        raise RuntimeError("The shared admin session store is unavailable") from None
