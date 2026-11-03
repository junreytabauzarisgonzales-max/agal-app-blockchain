import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    phone_number: str | None = None
    municipality: str | None = None


class UserUpdate(BaseModel):
    """All fields optional -- only the ones a client actually sends get changed."""

    full_name: str | None = None
    phone_number: str | None = None
    municipality: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    phone_number: str | None
    municipality: str | None
    is_active: bool
    created_at: datetime
