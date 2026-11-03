from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.url import async_database_url

def engine_options(*, serverless: bool, postgres: bool) -> dict:
    options = {"echo": settings.ENVIRONMENT == "development", "pool_pre_ping": True}
    if serverless:
        options["poolclass"] = NullPool
        if postgres:
            # Serverless instances and transaction poolers must not share
            # process-local asyncpg connection/prepared-statement state.
            options["connect_args"] = {"statement_cache_size": 0, "prepared_statement_cache_size": 0}
    return options


database_url = async_database_url(settings.DATABASE_URL)
engine = create_async_engine(database_url, **engine_options(serverless=settings.VERCEL, postgres=database_url.get_backend_name() == "postgresql"))

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
