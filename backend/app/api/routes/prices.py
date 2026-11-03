from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.price import PriceRecord
from app.models.user import User
from app.schemas.price import PriceRecordCreate, PriceRecordRead

router = APIRouter(prefix="/prices", tags=["prices"])


@router.post("", response_model=PriceRecordRead, status_code=201)
async def create_price_record(
    payload: PriceRecordCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.SUPPLIER, UserRole.BUYER)),
) -> PriceRecord:
    record = PriceRecord(**payload.model_dump(), posted_by_id=user.id)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("", response_model=list[PriceRecordRead])
async def list_price_records(
    species: str | None = Query(default=None),
    municipality: str | None = Query(default=None),
    since: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[PriceRecord]:
    # The phone labels this screen "Today's Buying Prices". Scheduled future
    # offers must not appear as prices that farmers can sell at today.
    today = datetime.now(timezone(timedelta(hours=8))).date()
    stmt = select(PriceRecord).where(PriceRecord.effective_date <= today).order_by(
        PriceRecord.effective_date.desc(), PriceRecord.created_at.desc(), PriceRecord.id)
    if species is not None:
        stmt = stmt.where(PriceRecord.species == species)
    if municipality is not None:
        stmt = stmt.where(PriceRecord.municipality == municipality)
    if since is not None:
        stmt = stmt.where(PriceRecord.effective_date >= since)
    result = await db.execute(stmt)
    return list(result.scalars().all())
