import asyncio
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import OnChainStatus
from app.services import chain_anchor, web3_client
from app.services.chain_hash import compute_event_hash, uuid_to_bytes32
from tests.test_admin_resources import add_batch, add_event, add_user


@pytest.fixture
def rpc(monkeypatch):
    w3, contract = MagicMock(), MagicMock()
    w3.eth.chain_id = 11155111
    w3.eth.account.from_key.return_value.address = "0x" + "12" * 20
    w3.eth.account.from_key.return_value.sign_transaction.return_value.raw_transaction = b"signed"
    w3.eth.send_raw_transaction.return_value = b"\xab" * 32
    w3.eth.wait_for_transaction_receipt.return_value = {"status": 1, "transactionHash": b"\xab" * 32, "blockNumber": 123}
    contract.functions.getRecord.return_value.call.return_value = (bytes(32), bytes(32), 0, False)
    monkeypatch.setattr(web3_client, "get_web3", lambda **_: w3)
    monkeypatch.setattr(web3_client, "get_contract", lambda _: contract)
    return w3, contract


def test_successful_ledger_receipt_uses_pending_nonce(rpc):
    w3, _ = rpc
    result = web3_client.record_event_on_chain(uuid4(), uuid4(), b"x" * 32)
    assert result == {"tx_hash": "0x" + "ab" * 32, "block_number": 123}
    w3.eth.get_transaction_count.assert_called_once_with("0x" + "12" * 20, "pending")


def test_reverted_receipt_is_never_reported_as_anchored(rpc):
    w3, _ = rpc
    w3.eth.wait_for_transaction_receipt.return_value["status"] = 0
    with pytest.raises(RuntimeError, match="reverted"):
        web3_client.record_event_on_chain(uuid4(), uuid4(), b"x" * 32)


def test_recover_already_mined_event_without_resending_or_overwriting(rpc):
    w3, contract = rpc
    batch_id = uuid4()
    contract.functions.getRecord.return_value.call.return_value = (uuid_to_bytes32(batch_id), b"x" * 32, 1, True)
    assert web3_client.record_event_on_chain(uuid4(), batch_id, b"x" * 32) == {"tx_hash": None, "block_number": None}
    w3.eth.send_raw_transaction.assert_not_called()
    with pytest.raises(RuntimeError, match="does not match"):
        web3_client.record_event_on_chain(uuid4(), batch_id, b"y" * 32)
    w3.eth.send_raw_transaction.assert_not_called()


def test_concurrent_background_threads_do_not_reuse_a_wallet_nonce(rpc):
    import time
    w3, contract = rpc
    next_nonce = [0]
    used = []
    def nonce(*_):
        value = next_nonce[0]
        time.sleep(0.01)  # exposes a read-then-send race without wallet serialization
        return value
    def build(transaction):
        used.append(transaction["nonce"])
        return transaction
    def send(_):
        next_nonce[0] += 1
        return b"\xab" * 32
    w3.eth.get_transaction_count.side_effect = nonce
    contract.functions.recordEvent.return_value.build_transaction.side_effect = build
    w3.eth.send_raw_transaction.side_effect = send
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: web3_client.record_event_on_chain(uuid4(), uuid4(), b"x" * 32), range(2)))
    assert used == [0, 1] and len(results) == 2


def test_durable_worker_recovers_pending_and_failed_events(db_session_factory, monkeypatch):
    engine = create_async_engine(str(db_session_factory.kw["bind"].url).replace("sqlite:", "sqlite+aiosqlite:"), poolclass=NullPool)
    monkeypatch.setattr(chain_anchor, "AsyncSessionLocal", async_sessionmaker(engine, expire_on_commit=False))
    calls = []
    def record(event_id, *_):
        calls.append(event_id)
        return {"tx_hash": "0x" + "ab" * 32, "block_number": 123}
    monkeypatch.setattr(chain_anchor, "record_event_on_chain", record)
    with db_session_factory() as db:
        farmer = add_user(db)
        for state in (OnChainStatus.PENDING, OnChainStatus.FAILED, OnChainStatus.ANCHORED):
            add_event(db, add_batch(db, farmer), farmer, state)
        db.commit()
    assert asyncio.run(chain_anchor.anchor_pending_events(retry_failed=True)) == 2
    assert len(calls) == 2
    with db_session_factory() as db:
        assert all(e.on_chain_status == OnChainStatus.ANCHORED for e in db.scalars(select(ChainOfCustodyEvent)))
    assert asyncio.run(chain_anchor.anchor_pending_events(retry_failed=True)) == 0
    asyncio.run(engine.dispose())


def test_event_hash_is_stable_for_json_key_order_and_detects_changes():
    from datetime import datetime, timezone
    from app.models.enums import CustodyEventType
    event = SimpleNamespace(id=uuid4(), batch_id=uuid4(), actor_id=uuid4(), event_type=CustodyEventType.NOTE_ADDED,
                            occurred_at=datetime(2026, 9, 1, tzinfo=timezone.utc), payload={"shipment_id": "demo", "weight": 400})
    expected = compute_event_hash(event)
    event.payload = {"weight": 400, "shipment_id": "demo"}
    assert compute_event_hash(event) == expected
    event.payload["weight"] = 401
    assert compute_event_hash(event) != expected
