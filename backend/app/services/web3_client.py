"""Signs and sends `recordEvent` transactions to HarvestLedger.

Every call here is synchronous/blocking (web3.py's HTTPProvider does plain
network I/O) and must only ever run off the event loop -- see
services.chain_anchor, which wraps calls into this module in
`asyncio.to_thread`. Farmers/suppliers never reach this module; it's only
invoked by the backend's own background anchoring task, signing with the
service wallet configured via SERVICE_WALLET_PRIVATE_KEY.
"""

import json
from functools import lru_cache
from pathlib import Path
from threading import Lock
from uuid import UUID

from web3 import Web3
from web3.contract import Contract

from app.core.config import settings
from app.services.chain_hash import uuid_to_bytes32

_ABI_PATH = Path(__file__).parent / "contracts" / "harvest_ledger_abi.json"
_wallet_lock = Lock()


@lru_cache
def _abi() -> list[dict]:
    return json.loads(_ABI_PATH.read_text())


def _require_configured(*, need_wallet: bool) -> None:
    required = {
        "WEB3_PROVIDER_URL": settings.WEB3_PROVIDER_URL,
        "HARVEST_LEDGER_ADDRESS": settings.HARVEST_LEDGER_ADDRESS,
    }
    if need_wallet:
        required["SERVICE_WALLET_PRIVATE_KEY"] = settings.SERVICE_WALLET_PRIVATE_KEY
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"web3 integration is not configured: missing {', '.join(missing)}")


def get_web3(*, need_wallet: bool = True) -> Web3:
    """`need_wallet=False` for read-only calls (e.g. verification) that
    anyone could make without a signing key -- recordEvent still requires
    the service wallet, but getRecord doesn't.
    """
    _require_configured(need_wallet=need_wallet)
    return Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL, request_kwargs={"timeout": 20}))


def get_contract(w3: Web3) -> Contract:
    return w3.eth.contract(address=settings.HARVEST_LEDGER_ADDRESS, abi=_abi())


def to_hex0x(value: bytes) -> str:
    return "0x" + value.hex().removeprefix("0x")


def record_event_on_chain(event_id: UUID, batch_id: UUID, data_hash: bytes) -> dict:
    """Blocks until the transaction is mined. Raises on failure -- the
    caller (chain_anchor.anchor_event) is responsible for catching that and
    marking the event's on_chain_status as FAILED rather than crashing.
    """
    # A pending DB event can already be on-chain if the process died after
    # mining, but before committing its status. Reconcile rather than sending
    # a transaction that the append-only contract will necessarily reject.
    with _wallet_lock:
        w3 = get_web3()
        contract = get_contract(w3)
        stored_batch, stored_hash, _, exists = contract.functions.getRecord(uuid_to_bytes32(event_id)).call()
        if exists:
            if bytes(stored_batch) != uuid_to_bytes32(batch_id) or bytes(stored_hash) != bytes(data_hash):
                raise RuntimeError("The ledger record does not match this event")
            # getRecord does not expose the original transaction/block. These
            # are nullable API fields; live verification remains independent.
            return {"tx_hash": None, "block_number": None}
        account = w3.eth.account.from_key(settings.SERVICE_WALLET_PRIVATE_KEY)
        tx = contract.functions.recordEvent(uuid_to_bytes32(event_id), uuid_to_bytes32(batch_id), data_hash).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address, "pending"),
            "chainId": w3.eth.chain_id,
        })
        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120, poll_latency=2)
        if receipt.get("status") != 1:
            raise RuntimeError("The ledger transaction reverted")
        return {"tx_hash": to_hex0x(receipt["transactionHash"]), "block_number": receipt["blockNumber"]}


def get_record(event_id: UUID) -> dict:
    """Read-only lookup of what's *actually* anchored on-chain for this
    event -- no wallet/signing needed, anyone could call this against
    Sepolia directly. This is what independent verification is built on,
    as opposed to just trusting the backend's own cached `on_chain_status`
    column.
    """
    w3 = get_web3(need_wallet=False)
    contract = get_contract(w3)
    batch_id_bytes, data_hash_bytes, recorded_at, exists = contract.functions.getRecord(
        uuid_to_bytes32(event_id)
    ).call()
    return {
        "exists": exists,
        "batch_id_hex": to_hex0x(batch_id_bytes),
        "data_hash_hex": to_hex0x(data_hash_bytes),
        "recorded_at": recorded_at,
    }
