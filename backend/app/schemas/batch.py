import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import BatchStatus
from app.schemas.common import as_utc


class BatchCreate(BaseModel):
    """Shape of a BATCH_CREATED item, whether it arrives via /sync or POST /batches directly."""

    id: uuid.UUID
    species: str = Field(min_length=1, max_length=255)
    estimated_weight_kg: Decimal = Field(ge=Decimal("0.01"), le=Decimal("99999999.99"))
    unit: str = Field(default="kg", min_length=1, max_length=16)
    harvest_latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    harvest_longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    harvested_at: datetime

    _utc = field_validator("harvested_at")(as_utc)

    @model_validator(mode="after")
    def coordinates_are_a_pair(self):
        if (self.harvest_latitude is None) != (self.harvest_longitude is None):
            raise ValueError("Latitude and longitude must be supplied together")
        if not self.species.strip():
            raise ValueError("Species must not be blank")
        return self


class BatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    farmer_id: uuid.UUID
    species: str
    estimated_weight_kg: Decimal
    unit: str
    harvest_latitude: Decimal | None
    harvest_longitude: Decimal | None
    harvested_at: datetime
    status: BatchStatus
    current_holder_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime
