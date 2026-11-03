from sqlalchemy.engine import URL, make_url


def async_database_url(value: str) -> URL:
    """Accept provider-issued PostgreSQL URLs, including Neon/libpq SSL options."""
    url = make_url(value)
    if url.drivername in {"postgres", "postgresql", "postgresql+asyncpg"}:
        query = dict(url.query)
        sslmode = query.pop("sslmode", None)
        if sslmode is not None:
            query.setdefault("ssl", sslmode)
        # This is a libpq client option, not an asyncpg.connect parameter.
        query.pop("channel_binding", None)
        url = url.set(drivername="postgresql+asyncpg", query=query)
    return url
