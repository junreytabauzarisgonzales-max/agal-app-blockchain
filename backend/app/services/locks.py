"""Transaction-scoped serialization for client-generated UUIDs on PostgreSQL.

Unlike a Python mutex, advisory locks work across API and worker processes.
SQLite tests use their own isolated databases; PostgreSQL is the runtime DB.
"""
import hashlib
from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def lock_ids(db: AsyncSession, namespace: str, ids: Iterable[UUID | str]) -> None:
    if db.get_bind().dialect.name != "postgresql":
        return
    for value in sorted({str(value) for value in ids}):
        key = int.from_bytes(hashlib.blake2b(f"agal:{namespace}:{value}".encode(), digest_size=8).digest(), "big", signed=True)
        await db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})
