import hmac

from fastapi import APIRouter, Header, HTTPException, Response

from app.core.config import settings
from app.services.chain_anchor import anchor_pending_events

router = APIRouter(prefix="/internal/cron", include_in_schema=False)


@router.get("/chain-anchors")
async def recover_chain_anchors(response: Response, authorization: str | None = Header(default=None)) -> dict:
    if not settings.CRON_SECRET or not hmac.compare_digest((authorization or "").encode(), f"Bearer {settings.CRON_SECRET}".encode()):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not all((settings.WEB3_PROVIDER_URL, settings.HARVEST_LEDGER_ADDRESS, settings.SERVICE_WALLET_PRIVATE_KEY)):
        raise HTTPException(status_code=503, detail="Blockchain anchoring is not configured")
    response.headers["Cache-Control"] = "no-store"
    # One receipt can take up to 120 seconds; keep recovery bounded within the
    # 300-second Vercel function budget. Normal writes still anchor immediately.
    checked = await anchor_pending_events(limit=1, retry_failed=True)
    return {"status": "ok", "checked": checked}
