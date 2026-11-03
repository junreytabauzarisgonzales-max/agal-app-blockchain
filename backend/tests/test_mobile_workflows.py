"""Requests and payloads used by the current Flutter screens, against a fake DB/chain."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select

from app.core.security import create_access_token
from app.models.batch import HarvestBatch
from app.models.custody_event import ChainOfCustodyEvent
from app.models.enums import UserRole
from app.models.message import Message
from app.services.chain_hash import compute_event_hash, uuid_to_bytes32
from app.services.web3_client import to_hex0x
from tests.test_admin_resources import add_user


@pytest.fixture
def mobile(client, db_session_factory, monkeypatch):
    with db_session_factory() as db:
        users = {name: add_user(db, name=name, role=role) for name, role in [
            ("farmer", UserRole.FARMER), ("other_farmer", UserRole.FARMER),
            ("supplier", UserRole.SUPPLIER), ("buyer", UserRole.BUYER),
        ]}
        db.commit()
    queued = []

    async def fake_anchor(event_id):
        queued.append(event_id)

    for route in ("batches", "custody_events", "sync"):
        monkeypatch.setattr(f"app.api.routes.{route}.anchor_event", fake_anchor)
    return client, users, queued, db_session_factory


def headers(users, name):
    return {"Authorization": f"Bearer {create_access_token(users[name].id)}"}


def batch_payload(weight="180"):
    return {"id": str(uuid.uuid4()), "species": "Eucheuma Cottonii (Sakol)", "estimated_weight_kg": weight,
            "unit": "kg", "harvested_at": "2026-09-01T08:00:00+08:00",
            "harvest_latitude": 5.029, "harvest_longitude": 119.773}


def event_payload(batch_id, kind, hour=1, payload=None):
    return {"id": str(uuid.uuid4()), "batch_id": batch_id, "event_type": kind,
            "occurred_at": f"2026-09-01T{hour:02}:00:00Z", "payload": payload or {}}


def post_event(mobile, batch_id, kind, actor="farmer", hour=1, payload=None):
    client, users, _, _ = mobile
    return client.post("/custody-events", json=event_payload(batch_id, kind, hour, payload), headers=headers(users, actor))


def create_ready_batch(mobile, weight="180"):
    client, users, _, _ = mobile
    payload = batch_payload(weight)
    response = client.post("/batches", json=payload, headers=headers(users, "farmer"))
    assert response.status_code == 201, response.text
    batch_id = payload["id"]
    assert post_event(mobile, batch_id, "drying_started", hour=1).status_code == 201
    assert post_event(mobile, batch_id, "drying_completed", hour=2).status_code == 201
    return batch_id


QUALITY = {"verified_weight_kg": 175.5, "moisture_percent": 22, "quality_grade": "excellent", "remarks": "Dry and clean"}


def test_mobile_offline_harvest_handover_purchase_and_verification(mobile, monkeypatch):
    client, users, queued, factory = mobile
    harvest = batch_payload()
    items = [{**harvest, "type": "batch_created"},
             {**event_payload(harvest["id"], "drying_started", 1), "type": "custody_event"},
             {**event_payload(harvest["id"], "drying_completed", 2), "type": "custody_event"}]
    response = client.post("/sync", json={"items": items}, headers=headers(users, "farmer"))
    assert response.status_code == 200, response.text
    assert [r["status"] for r in response.json()["results"]] == ["created"] * 3
    replay = client.post("/sync", json={"items": items}, headers=headers(users, "farmer"))
    assert [r["status"] for r in replay.json()["results"]] == ["duplicate"] * 3
    ready = client.get("/batches", params={"status": "dried"}, headers=headers(users, "supplier")).json()
    assert [b["id"] for b in ready] == [harvest["id"]]
    for actor, transfer, hour in [("supplier", "transferred_to_supplier", 3), ("buyer", "transferred_to_buyer", 5)]:
        assert post_event(mobile, harvest["id"], "quality_graded", actor, hour, QUALITY).status_code == 201
        receipt = post_event(mobile, harvest["id"], transfer, actor, hour + 1, QUALITY)
        assert receipt.status_code == 201, receipt.text
    assert post_event(mobile, harvest["id"], "payment_recorded", "supplier", 7, {"amount_php": 9900}).status_code == 201
    assert post_event(mobile, harvest["id"], "exported", "buyer", 8).status_code == 201
    batch = client.get(f"/batches/{harvest['id']}", headers=headers(users, "buyer")).json()
    assert batch["status"] == "exported" and batch["current_holder_id"] == str(users["buyer"].id)
    history = client.get(f"/batches/{harvest['id']}/events", headers=headers(users, "buyer")).json()
    assert len(history) == 9 and len(queued) == 9
    with factory() as db:
        event = db.get(ChainOfCustodyEvent, uuid.UUID(history[0]["id"]))
        record = {"exists": True, "data_hash_hex": to_hex0x(compute_event_hash(event)),
                  "batch_id_hex": to_hex0x(uuid_to_bytes32(event.batch_id)), "recorded_at": 1788220800}
    monkeypatch.setattr("app.api.routes.custody_events.get_record", lambda _: record)
    verified = client.get(f"/custody-events/{history[0]['id']}/verify", headers=headers(users, "buyer"))
    assert verified.status_code == 200 and verified.json()["verified"] is True
    record["data_hash_hex"] = "0x" + "00" * 32
    assert client.get(f"/custody-events/{history[0]['id']}/verify", headers=headers(users, "buyer")).json()["verified"] is False


def test_roles_and_current_state_control_custody(mobile):
    client, users, _, _ = mobile
    batch_id = create_ready_batch(mobile)
    assert post_event(mobile, batch_id, "transferred_to_buyer", "other_farmer", 3).status_code == 403
    assert post_event(mobile, batch_id, "drying_started", "other_farmer", 3).status_code == 403
    assert post_event(mobile, batch_id, "transferred_to_buyer", "buyer", 3).status_code == 409
    assert post_event(mobile, batch_id, "transferred_to_supplier", "supplier", 3).status_code == 201
    assert post_event(mobile, batch_id, "transferred_to_supplier", "supplier", 4).status_code == 409
    assert post_event(mobile, batch_id, "note_added", "other_farmer", 4, {"notes": "unrelated"}).status_code == 403
    assert client.post("/sync", json={"items": []}, headers=headers(users, "buyer")).status_code == 403


def test_delayed_offline_drying_is_logged_without_regressing_inventory(mobile):
    client, users, _, _ = mobile
    batch_id = create_ready_batch(mobile)
    assert post_event(mobile, batch_id, "transferred_to_supplier", "supplier", 3).status_code == 201
    before = client.get(f"/batches/{batch_id}", headers=headers(users, "supplier")).json()
    late = post_event(mobile, batch_id, "drying_started", "farmer", 1)
    assert late.status_code == 201, late.text
    after = client.get(f"/batches/{batch_id}", headers=headers(users, "supplier")).json()
    assert after["status"] == "with_supplier" and after["current_holder_id"] == str(users["supplier"].id)
    assert after["version"] == before["version"] + 1
    assert post_event(mobile, batch_id, "drying_started", "farmer", 4).status_code == 403


def test_online_handover_retry_preserves_first_timestamp_and_uuid(mobile):
    client, users, _, factory = mobile
    batch_id = create_ready_batch(mobile)
    payload = event_payload(batch_id, "transferred_to_supplier", 3, QUALITY)
    first = client.post("/custody-events", json=payload, headers=headers(users, "supplier"))
    assert first.status_code == 201
    payload["occurred_at"] = "2026-09-01T04:00:00Z"
    retry = client.post("/custody-events", json=payload, headers=headers(users, "supplier"))
    assert retry.status_code == 201 and retry.json()["occurred_at"] == first.json()["occurred_at"]
    payload["payload"] = {**QUALITY, "verified_weight_kg": 190}
    assert client.post("/custody-events", json=payload, headers=headers(users, "supplier")).status_code == 409
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(ChainOfCustodyEvent).where(ChainOfCustodyEvent.batch_id == uuid.UUID(batch_id))) == 4


def test_sync_bad_item_does_not_rollback_other_harvests_or_messages(mobile):
    client, users, _, factory = mobile
    harvest = batch_payload()
    message = {"type": "message_sent", "id": str(uuid.uuid4()), "recipient_id": str(users["supplier"].id),
               "body": "Ready for pickup", "occurred_at": "2026-09-01T03:00:00Z"}
    bad = {**event_payload(str(uuid.uuid4()), "drying_started"), "type": "custody_event"}
    response = client.post("/sync", json={"items": [{**harvest, "type": "batch_created"}, bad, message]}, headers=headers(users, "farmer"))
    assert response.status_code == 200
    assert [r["status"] for r in response.json()["results"]] == ["created", "error", "created"]
    with factory() as db:
        assert db.get(HarvestBatch, uuid.UUID(harvest["id"])) is not None
        assert db.get(Message, uuid.UUID(message["id"])) is not None


def test_duplicate_uuids_do_not_expose_other_accounts_messages_or_harvests(mobile):
    client, users, _, _ = mobile
    harvest = batch_payload()
    assert client.post("/batches", json=harvest, headers=headers(users, "farmer")).status_code == 201
    assert client.post("/batches", json=harvest, headers=headers(users, "other_farmer")).status_code == 409
    message = {"id": str(uuid.uuid4()), "recipient_id": str(users["supplier"].id), "body": "Private harvest agreement", "occurred_at": "2026-09-01T03:00:00Z"}
    assert client.post("/messages", json=message, headers=headers(users, "farmer")).status_code == 201
    assert client.post("/messages", json=message, headers=headers(users, "farmer")).status_code == 201
    response = client.post("/messages", json=message, headers=headers(users, "buyer"))
    assert response.status_code == 409 and message["body"] not in response.text
    assert client.get(f"/messages/with/{users['farmer'].id}", headers=headers(users, "buyer")).json() == []


def test_flutter_shipment_notes_validate_membership_weight_and_publish_to_history(mobile):
    client, users, queued, _ = mobile
    ids = [create_ready_batch(mobile, weight) for weight in ("180", "220")]
    for batch_id in ids:
        assert post_event(mobile, batch_id, "transferred_to_supplier", "supplier", 3).status_code == 201
    manifest = {"notes": "Bundled into shipment", "shipment_id": str(uuid.uuid4()), "destination": "Zamboanga warehouse",
                "shipment_batch_ids": ids, "shipment_weight_kg": 400.0}
    before = len(queued)
    for batch_id in ids:
        response = post_event(mobile, batch_id, "note_added", "supplier", 4, manifest)
        assert response.status_code == 201, response.text
        history = client.get(f"/batches/{batch_id}/events", headers=headers(users, "buyer")).json()
        assert history[-1]["payload"] == manifest
    assert len(queued) == before + 2
    assert post_event(mobile, ids[0], "note_added", "supplier", 4, {**manifest, "destination": "Changed warehouse"}).status_code == 409
    assert post_event(mobile, ids[0], "note_added", "supplier", 4, {**manifest, "shipment_id": str(uuid.uuid4()), "shipment_weight_kg": 401}).status_code == 422
    assert post_event(mobile, ids[0], "note_added", "farmer", 4, manifest).status_code == 403
    foreign = create_ready_batch(mobile, "50")
    assert post_event(mobile, ids[0], "note_added", "supplier", 4, {**manifest, "shipment_id": str(uuid.uuid4()), "shipment_batch_ids": [ids[0], foreign], "shipment_weight_kg": 230}).status_code == 403


@pytest.mark.parametrize("invalid", [{**QUALITY, "moisture_percent": 101}, {**QUALITY, "verified_weight_kg": -5}, {**QUALITY, "quality_grade": "invented"}])
def test_bad_quality_measurements_are_rejected(mobile, invalid):
    batch_id = create_ready_batch(mobile)
    assert post_event(mobile, batch_id, "quality_graded", "supplier", 3, invalid).status_code == 422


def test_buying_prices_exclude_scheduled_future_offers(mobile):
    client, users, _, _ = mobile
    today = datetime.now(timezone(timedelta(hours=8))).date()
    for offset, price in [(0, "55.00"), (1, "999.00")]:
        response = client.post("/prices", json={"species": "Cottonii", "price_per_kg": price, "effective_date": str(today + timedelta(days=offset))}, headers=headers(users, "supplier"))
        assert response.status_code == 201
    prices = client.get("/prices", headers=headers(users, "farmer")).json()
    assert len(prices) == 1 and prices[0]["price_per_kg"] == "55.00"


def test_verification_errors_do_not_echo_rpc_credentials(mobile, monkeypatch):
    client, users, _, _ = mobile
    batch_id = create_ready_batch(mobile)
    def unreachable(_):
        raise RuntimeError("https://private-rpc.example/?key=should-not-be-visible")
    monkeypatch.setattr("app.api.routes.custody_events.get_record", unreachable)
    response = client.get(f"/custody-events/{batch_id}/verify", headers=headers(users, "buyer"))
    assert response.status_code == 502 and "should-not-be-visible" not in response.text
