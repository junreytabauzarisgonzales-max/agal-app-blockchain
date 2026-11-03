import enum


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    SUPPLIER = "supplier"
    BUYER = "buyer"


class BatchStatus(str, enum.Enum):
    """Current-state projection, derived by folding a batch's custody events."""

    HARVESTED = "harvested"
    DRYING = "drying"
    DRIED = "dried"
    WITH_SUPPLIER = "with_supplier"
    WITH_BUYER = "with_buyer"
    EXPORTED = "exported"
    REJECTED = "rejected"


class CustodyEventType(str, enum.Enum):
    """Every state change to a batch is one of these, appended never mutated.

    BATCH_CREATED is the special first event for a batch: it both creates the
    HarvestBatch projection row and the corresponding event record. New event
    types can be added over time (a migration to extend the DB enum), but
    existing rows are never edited or removed.
    """

    BATCH_CREATED = "batch_created"
    DRYING_STARTED = "drying_started"
    DRYING_COMPLETED = "drying_completed"
    QUALITY_GRADED = "quality_graded"
    TRANSFERRED_TO_SUPPLIER = "transferred_to_supplier"
    TRANSFERRED_TO_BUYER = "transferred_to_buyer"
    PRICE_AGREED = "price_agreed"
    PAYMENT_RECORDED = "payment_recorded"
    EXPORTED = "exported"
    REJECTED = "rejected"
    NOTE_ADDED = "note_added"


class OnChainStatus(str, enum.Enum):
    """Whether a custody event's hash has been anchored on HarvestLedger yet.

    Written by the backend's web3.py integration (a later milestone) --
    every event starts PENDING the moment it's persisted.
    """

    PENDING = "pending"
    ANCHORED = "anchored"
    FAILED = "failed"
