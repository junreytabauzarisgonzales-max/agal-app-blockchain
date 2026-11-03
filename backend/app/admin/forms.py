"""Server-side validation and persistence for the editable admin resources
(users, price records). Validation reuses the app's own schemas where they
exist; the admin variants add the length limits the DB columns enforce.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, EmailStr, ValidationError, field_validator
from pydantic import Field as PField
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.price import PriceRecord
from app.models.user import User
from app.schemas.price import PriceRecordCreate

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_BYTES = 72  # bcrypt ignores anything past this, so refuse instead of silently truncating


@dataclass(frozen=True)
class Field:
    name: str
    label: str
    type: str = "text"  # text | email | password | number | date | select | checkbox | textarea
    required: bool = False
    help: str = ""
    options: tuple[tuple[str, str], ...] = ()  # (value, label) for selects
    step: str = ""
    autocomplete: str = ""


def _blank_to_none(value: Any) -> Any:
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _errors(exc: ValidationError) -> dict[str, str]:
    result: dict[str, str] = {}
    for err in exc.errors():
        name = str(err["loc"][0]) if err["loc"] else "_form"
        if err.get("input") is None or err.get("type") == "missing":
            message = "This field is required."
        else:
            message = err["msg"]
        result.setdefault(name, message)
    return result


# --- users ------------------------------------------------------------------

class UserForm(BaseModel):
    email: EmailStr
    full_name: str = PField(min_length=1, max_length=255)
    role: UserRole
    phone_number: str | None = PField(default=None, max_length=32)
    municipality: str | None = PField(default=None, max_length=255)
    is_active: bool = False
    password: str | None = None

    _strip = field_validator("*", mode="before")(_blank_to_none)

    @field_validator("email")
    @classmethod
    def _lower_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def _password_rules(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
            raise ValueError(f"Password must be at most {MAX_PASSWORD_BYTES} bytes.")
        return value


class UserFormSpec:
    def fields(self, obj: User | None) -> tuple[Field, ...]:
        password_help = (
            "Leave blank to keep the current password." if obj else f"At least {MIN_PASSWORD_LENGTH} characters."
        )
        return (
            Field("full_name", "Full name", required=True),
            Field("email", "Email", "email", required=True, autocomplete="off"),
            Field("role", "Role", "select", required=True, options=tuple((r.value, r.value.title()) for r in UserRole)),
            Field("phone_number", "Phone number"),
            Field("municipality", "Municipality"),
            Field("password", "New password" if obj else "Password", "password", required=obj is None,
                  help=password_help, autocomplete="new-password"),
            Field("is_active", "Active account", "checkbox", help="Inactive users cannot use the app."),
        )

    def initial(self, obj: User | None) -> dict[str, Any]:
        if obj is None:
            return {"role": UserRole.FARMER.value, "is_active": True}
        return {
            "full_name": obj.full_name,
            "email": obj.email,
            "role": obj.role.value,
            "phone_number": obj.phone_number or "",
            "municipality": obj.municipality or "",
            "is_active": obj.is_active,
        }

    async def validate(
        self, db: AsyncSession, raw: dict[str, Any], obj: User | None
    ) -> tuple[UserForm | None, dict[str, str]]:
        try:
            cleaned = UserForm(**raw)
        except ValidationError as exc:
            return None, _errors(exc)
        errors: dict[str, str] = {}
        if obj is None and cleaned.password is None:
            errors["password"] = "This field is required."
        taken = await db.scalar(select(User.id).where(User.email == cleaned.email))
        if taken is not None and (obj is None or taken != obj.id):
            errors["email"] = "This email is already registered."
        return (None if errors else cleaned), errors

    async def create(self, db: AsyncSession, cleaned: UserForm) -> User:
        assert cleaned.password is not None
        user = User(
            email=cleaned.email,
            hashed_password=hash_password(cleaned.password),
            full_name=cleaned.full_name,
            role=cleaned.role,
            phone_number=cleaned.phone_number,
            municipality=cleaned.municipality,
            is_active=cleaned.is_active,
        )
        db.add(user)
        await db.flush()  # assigns the id; the caller commits (together with its audit row)
        return user

    async def update(self, db: AsyncSession, obj: User, cleaned: UserForm) -> None:
        obj.email = cleaned.email
        obj.full_name = cleaned.full_name
        obj.role = cleaned.role
        obj.phone_number = cleaned.phone_number
        obj.municipality = cleaned.municipality
        obj.is_active = cleaned.is_active
        if cleaned.password is not None:
            obj.hashed_password = hash_password(cleaned.password)
        await db.flush()


# --- price records -----------------------------------------------------------

class PriceForm(PriceRecordCreate):
    """The app's own PriceRecordCreate, plus DB-column limits and who posted it."""

    species: str = PField(min_length=1, max_length=255)
    grade: str | None = PField(default=None, max_length=64)
    price_per_kg: Decimal = PField(gt=0, max_digits=10, decimal_places=2)
    currency: str = PField(default="PHP", pattern=r"^[A-Za-z]{3}$")
    municipality: str | None = PField(default=None, max_length=255)
    notes: str | None = PField(default=None, max_length=5000)
    posted_by_email: EmailStr

    _strip = field_validator("*", mode="before")(_blank_to_none)

    @field_validator("currency")
    @classmethod
    def _upper_currency(cls, value: str) -> str:
        return value.upper()

    @field_validator("posted_by_email")
    @classmethod
    def _lower_email(cls, value: str) -> str:
        return value.lower()


@dataclass
class PriceValues:
    """Validated price fields plus the resolved poster."""

    form: PriceForm
    poster: User = field(repr=False)


class PriceFormSpec:
    def fields(self, obj: PriceRecord | None) -> tuple[Field, ...]:
        return (
            Field("species", "Species", required=True),
            Field("grade", "Grade"),
            Field("price_per_kg", "Price per kg", "number", required=True, step="0.01"),
            Field("currency", "Currency", required=True, help="3-letter code, e.g. PHP."),
            Field("municipality", "Municipality"),
            Field("effective_date", "Effective date", "date", required=True),
            Field("posted_by_email", "Posted by (email)", "email", required=True,
                  help="Must be an existing supplier or buyer account."),
            Field("notes", "Notes", "textarea"),
        )

    def initial(self, obj: PriceRecord | None) -> dict[str, Any]:
        if obj is None:
            return {"currency": "PHP"}
        return {
            "species": obj.species,
            "grade": obj.grade or "",
            "price_per_kg": str(obj.price_per_kg),
            "currency": obj.currency,
            "municipality": obj.municipality or "",
            "effective_date": obj.effective_date.isoformat(),
            "notes": obj.notes or "",
        }

    async def validate(
        self, db: AsyncSession, raw: dict[str, Any], obj: PriceRecord | None
    ) -> tuple[PriceValues | None, dict[str, str]]:
        try:
            cleaned = PriceForm(**raw)
        except ValidationError as exc:
            return None, _errors(exc)
        poster = await db.scalar(select(User).where(User.email == cleaned.posted_by_email))
        if poster is None:
            return None, {"posted_by_email": "No user with this email."}
        if poster.role not in (UserRole.SUPPLIER, UserRole.BUYER):
            return None, {"posted_by_email": "Only suppliers and buyers can post prices."}
        return PriceValues(cleaned, poster), {}

    async def create(self, db: AsyncSession, cleaned: PriceValues) -> PriceRecord:
        record = PriceRecord(**cleaned.form.model_dump(exclude={"posted_by_email"}), posted_by_id=cleaned.poster.id)
        db.add(record)
        await db.flush()
        return record

    async def update(self, db: AsyncSession, obj: PriceRecord, cleaned: PriceValues) -> None:
        for name, value in cleaned.form.model_dump(exclude={"posted_by_email"}).items():
            setattr(obj, name, value)
        obj.posted_by_id = cleaned.poster.id
        await db.flush()

    async def poster_email(self, db: AsyncSession, obj: PriceRecord) -> str:
        return await db.scalar(select(User.email).where(User.id == obj.posted_by_id)) or ""


FORMS: dict[str, Any] = {"users": UserFormSpec(), "prices": PriceFormSpec()}
