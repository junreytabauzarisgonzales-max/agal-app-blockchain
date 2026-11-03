"""Rules for the mobile app's existing custody and shipment-note payloads."""
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.batch import HarvestBatch
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import BatchStatus, CustodyEventType, UserRole
from app.models.user import User
from app.services.errors import ConflictError, ForbiddenError, DomainError
from app.services.locks import lock_ids


class PayloadError(DomainError):
    status_code = 422


class QualityPayload(BaseModel):
    model_config = ConfigDict(extra="allow")
    verified_weight_kg: Decimal = Field(gt=0, le=99999999.99)
    moisture_percent: Decimal = Field(ge=0, le=100)
    quality_grade: Literal["excellent", "good", "fair"]
    remarks: str = Field(default="", max_length=1000)


class ShipmentPayload(BaseModel):
    model_config = ConfigDict(extra="allow")
    shipment_id: UUID
    destination: str = Field(min_length=1, max_length=1000)
    shipment_batch_ids: list[UUID] = Field(min_length=1)
    shipment_weight_kg: Decimal = Field(gt=0)


async def validate_payload(db: AsyncSession, item, actor: User) -> None:
    payload = item.payload
    try:
        if item.event_type == CustodyEventType.QUALITY_GRADED:
            QualityPayload.model_validate(payload)
        elif item.event_type in {CustodyEventType.TRANSFERRED_TO_SUPPLIER, CustodyEventType.TRANSFERRED_TO_BUYER}:
            # Older clients only sent {}. The current handover screen also
            # sends the same quality measurements as the grading event.
            if any(key in payload for key in ("verified_weight_kg", "moisture_percent", "quality_grade")):
                QualityPayload.model_validate(payload)
        elif item.event_type == CustodyEventType.PAYMENT_RECORDED:
            value = payload.get("amount_php", payload.get("amount"))
            if value is None or isinstance(value, bool):
                raise ValueError("Payment requires amount_php or amount")
            amount = Decimal(str(value))
            if not amount.is_finite() or amount <= 0:
                raise ValueError("Payment amount must be positive and finite")
            if payload.get("currency", "PHP") != "PHP":
                raise ValueError("The mobile sales dashboard records PHP payments")
        elif item.event_type == CustodyEventType.NOTE_ADDED and "shipment_id" in payload:
            manifest = ShipmentPayload.model_validate(payload)
            ids = manifest.shipment_batch_ids
            if not manifest.destination.strip() or len(ids) != len(set(ids)) or item.batch_id not in ids:
                raise ValueError("Shipment requires a destination and unique batch ids including this batch")
            if actor.role != UserRole.SUPPLIER:
                raise ForbiddenError("Only a supplier can bundle inventory into a shipment")
            await lock_ids(db, "shipment", [manifest.shipment_id])
            previous = await db.scalar(select(ChainOfCustodyEvent).where(
                ChainOfCustodyEvent.event_type == CustodyEventType.NOTE_ADDED,
                ChainOfCustodyEvent.payload["shipment_id"].as_string() == str(manifest.shipment_id),
            ).limit(1))
            if previous is not None:
                old = ShipmentPayload.model_validate(previous.payload)
                if (previous.actor_id != actor.id or old.destination != manifest.destination
                        or set(old.shipment_batch_ids) != set(ids)
                        or old.shipment_weight_kg != manifest.shipment_weight_kg):
                    raise ConflictError("A shipment reference cannot be reused with different contents")
            batches = list((await db.scalars(select(HarvestBatch).where(HarvestBatch.id.in_(ids)))).all())
            if len(batches) != len(ids):
                raise ConflictError("One or more shipment batches do not exist")
            if any(b.current_holder_id != actor.id or b.status != BatchStatus.WITH_SUPPLIER for b in batches):
                raise ForbiddenError("Shipment batches must be in your supplier inventory")
            weight = sum((Decimal(str(b.estimated_weight_kg)) for b in batches), Decimal(0))
            if abs(manifest.shipment_weight_kg - weight) > Decimal("0.01"):
                raise ValueError("Shipment weight must match the selected inventory batches")
    except (ValidationError, ValueError, ArithmeticError) as exc:
        # No exception values or arbitrary submitted JSON are reflected into
        # the response. /sync returns this as an error for this item only.
        if isinstance(exc, ValidationError):
            detail = "Invalid quality or shipment payload"
        else:
            detail = str(exc)
        raise PayloadError(detail) from exc
