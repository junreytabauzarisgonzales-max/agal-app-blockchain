"""Computes the exact digest anchored on HarvestLedger for a custody event.

Deterministic and re-derivable by anyone who can fetch the event from the
API: recompute this and compare against the on-chain record (see
web3_client.get_record) to verify the event hasn't been altered after the
fact. See contract/README.md for the on-chain side of this contract.
"""

import json
from typing import Any
from uuid import UUID

from web3 import Web3

from app.models.custody_event import ChainOfCustodyEvent


def _canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def compute_event_hash(event: ChainOfCustodyEvent) -> bytes:
    payload_hash = Web3.keccak(text=_canonical_json(event.payload)).hex()
    canonical = _canonical_json(
        {
            "event_id": str(event.id),
            "batch_id": str(event.batch_id),
            "event_type": event.event_type.value,
            "actor_id": str(event.actor_id),
            "occurred_at": event.occurred_at.isoformat(),
            "payload_hash": payload_hash,
        }
    )
    return Web3.keccak(text=canonical)


def uuid_to_bytes32(value: UUID) -> bytes:
    """Right-justifies the UUID's 16 bytes into a 32-byte value -- the same
    zero-padding scheme as the contract test suite's `uuidToBytes32` helper
    (ethers' `zeroPadValue`), so eventId/batchId agree on both sides.
    """
    return value.bytes.rjust(32, b"\x00")
