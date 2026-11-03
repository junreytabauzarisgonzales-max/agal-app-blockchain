from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Imported so Alembic's autogenerate can discover every mapped model via
# Base.metadata, without each model module needing to be imported by hand.
from app.models import admin_audit_log, batch, custody_event, message, price, user  # noqa: E402,F401
