import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def read_current_user(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me", response_model=UserRead)
async def update_current_user(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> User:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/directory", response_model=list[UserRead])
async def list_directory(
    role: UserRole | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[User]:
    """Lets any authenticated account find counterparties to start a chat
    with (e.g. a Farmer looking up Suppliers). Deliberately minimal --
    no relationship/contact restriction yet, just a role filter.
    """
    stmt = select(User).where(User.is_active.is_(True)).order_by(User.full_name)
    if role is not None:
        stmt = stmt.where(User.role == role)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> User:
    """Public profile lookup -- e.g. so a chat thread can show who a
    conversation is with, including their phone number for the SMS
    fallback, without needing to already have exchanged messages.
    """
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
