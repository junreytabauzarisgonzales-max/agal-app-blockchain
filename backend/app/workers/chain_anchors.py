"""Run: python -m app.workers.chain_anchors --retry-failed [--once]."""
import argparse
import asyncio
import logging

from app.services.chain_anchor import anchor_pending_events


async def run(*, once: bool, limit: int, interval: int, retry_failed: bool) -> None:
    while True:
        try:
            count = await anchor_pending_events(limit, retry_failed=retry_failed)
            logging.getLogger(__name__).info("Checked %d custody events for anchoring", count)
        except Exception:
            logging.getLogger(__name__).exception("Anchoring sweep failed; committed events remain queued")
            if once:
                raise
        if once:
            return
        await asyncio.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Recover committed events awaiting blockchain anchoring")
    parser.add_argument("--once", action="store_true", help="Run one sweep (for cron)")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--interval", type=int, default=60)
    args = parser.parse_args()
    if args.limit < 1 or args.interval < 1:
        parser.error("limit and interval must be positive")
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run(once=args.once, limit=args.limit, interval=args.interval, retry_failed=args.retry_failed))


if __name__ == "__main__":
    main()
