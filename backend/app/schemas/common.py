from datetime import datetime, timezone


def as_utc(value: datetime) -> datetime:
    """Accept legacy naive timestamps as UTC; normalize device offsets once."""
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
