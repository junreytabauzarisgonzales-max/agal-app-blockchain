import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PriceRecordCreate(BaseModel):
    species: str = Field(min_length=1, max_length=255)
    grade: str | None = Field(default=None, max_length=64)
    price_per_kg: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    currency: str = Field(default="PHP", min_length=3, max_length=3)
    municipality: str | None = Field(default=None, max_length=255)
    effective_date: date
    notes: str | None = None


class PriceRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    species: str
    grade: str | None
    price_per_kg: Decimal
    currency: str
    municipality: str | None
    posted_by_id: uuid.UUID
    effective_date: date
    notes: str | None
    created_at: datetime
