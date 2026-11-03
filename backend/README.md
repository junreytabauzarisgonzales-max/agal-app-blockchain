# Agal API

For Vercel project settings, secret generation, hosted PostgreSQL, shared admin
sessions, and scheduled blockchain recovery, see [DEPLOYMENT.md](../DEPLOYMENT.md).

FastAPI backend for Agal, a price-transparency and traceability platform for
seaweed farmers, aggregators, and exporters in Tawi-Tawi.

## Data model

- **User** — `farmer` / `supplier` / `buyer`, one shared table with a `role` column.
- **PriceRecord** — a price point posted by a Supplier or Buyer. Plain CRUD;
  Supplier/Buyer roles assume normal connectivity, so this never goes through `/sync`.
- **HarvestBatch** — a read-model projection of a batch's *current* state
  (species, status, current holder, ...). Its `id` is client-generated
  (minted on-device by the Farmer app) and it is never edited directly by a
  request; it only changes by folding `ChainOfCustodyEvent` rows.
  `harvest_latitude`/`harvest_longitude` are captured from the device's GPS
  by the Farmer app (see `apps/agal`'s `LocationPicker`) rather than typed
  in as a free-text address.
- **Message** — a direct message between two accounts, immutable and
  append-only like `ChainOfCustodyEvent`. See the Endpoints list below.
- **ChainOfCustodyEvent** — the source of truth: an **immutable, append-only**
  log of everything that happens to a batch (harvested, dried, transferred,
  priced, paid, exported, ...). Its `id` is also client-generated, which is
  what makes `/sync` idempotent — replaying the same event is a no-op because
  the id already exists. This is also the unit of data that's hashed and
  anchored on the `HarvestLedger` contract (see `on_chain_status` /
  `on_chain_tx_hash` / `on_chain_block_number` columns).

## On-chain anchoring

Every successful `batch_created`/`custody_event` write (via `/sync`,
`/custody-events`, or `POST /batches`) schedules a `BackgroundTasks` job
(`app/services/chain_anchor.py`) that runs *after* the response is already
on its way back to the app, since a Sepolia confirmation can take several
seconds. That job:

1. Computes a canonical `keccak256` digest of the event (`app/services/chain_hash.py`) — no plaintext ever goes on-chain, only the hash.
2. Signs and sends a `HarvestLedger.recordEvent(eventId, batchId, dataHash)` transaction with the service wallet (`app/services/web3_client.py`), configured via `WEB3_PROVIDER_URL` / `HARVEST_LEDGER_ADDRESS` / `SERVICE_WALLET_PRIVATE_KEY`.
3. Updates the event's `on_chain_status` to `anchored` (with `on_chain_tx_hash` + `on_chain_block_number`) or `failed`.

See `contract/README.md` for what's actually stored on-chain and why.

**`GET /custody-events/{id}/verify`** is that independent verification,
already done for you: it re-fetches the record straight from the live
contract on Sepolia (`app/services/web3_client.py`'s `get_record`, a
read-only call, no wallet needed), recomputes the event's expected hash,
and reports whether they actually match -- rather than just returning the
backend's own cached `on_chain_status` column, which would be meaningless
as a trust signal since it's written by the same backend that wrote the
history. This is what the mobile app's "Verify on Sepolia" action calls.

### Why event-sourced instead of mutable rows + last-write-wins

The Farmer app is offline-first and syncs in the background, so the backend
needs a conflict-resolution story for records created/edited on a phone that
may have been offline for days. Rather than resolving conflicts between
competing edits to a mutable row, every action is stored as a new immutable
event (never updated, never deleted). That avoids overwriting competing edits:
sync inserts new event ids and checks their actor, payload, and custody transition. It
maps directly onto the chain-of-custody / on-chain-hashing requirement: each
event is exactly the unit that gets hashed.

## Endpoints

- `POST /auth/register`, `POST /auth/login` — JWT auth (`role` is part of the user).
- `GET /users/me`, `PATCH /users/me` — view/edit your own profile (full name, phone, municipality).
- `GET /users/directory?role=` — find counterparts to start a chat with.
- `GET /users/{id}` — public profile lookup (e.g. for a chat thread's header + SMS fallback number).
- `POST /prices`, `GET /prices` — Supplier/Buyer post prices; any authenticated role can read.
- `POST /batches`, `GET /batches` (optionally filtered by `farmer_id`/`holder_id`/`status`), `GET /batches/{id}`, `GET /batches/{id}/events` — direct/online batch + history access.
- `POST /custody-events` — direct/online custody event recording (e.g. a Supplier confirming receipt).
- `GET /custody-events/{id}/verify` — independently checks one event against the live Sepolia contract; see "On-chain anchoring" above.
- `POST /messages`, `GET /messages/threads`, `GET /messages/with/{user_id}`, `POST /messages/with/{user_id}/read` — direct messaging between any two accounts. Same append-only, client-generated-id idempotency pattern as custody events; a "thread" is just every message between two users, there's no separate conversation row.
- `POST /sync` — **Farmer-only**, idempotent bulk-apply endpoint for the offline queue. Accepts a list of `batch_created` / `custody_event` / `message_sent` items, each keyed by a client-generated UUID; replays of already-applied items come back as `"duplicate"` rather than erroring or double-applying.

## Mobile workflow rules

The existing mobile request URLs and response shapes are preserved.

- Farmers create harvests and record drying for their own batches. Suppliers
  confirm receipt of dried batches; buyers confirm receipt from suppliers.
  Receipt transfers custody to the authenticated receiving account.
- The mobile verification form can post `quality_graded` immediately before
  receipt. `verified_weight_kg` must be positive, `moisture_percent` must be
  between 0 and 100, and `quality_grade` is `excellent`, `good`, or `fair`.
- UUID retries are scoped to their original actor and intent. Another account
  cannot retrieve a private message by submitting its UUID. Online handover
  retries may regenerate `occurred_at`; the first accepted timestamp is kept.
- `/sync` returns `error` for a rejected business operation while committing
  other valid items. PostgreSQL transaction locks serialize concurrent
  retries and competing custody updates across API processes.
- Delayed farmer drying records that occurred before a recorded transfer can
  be added to the history without moving inventory back into farmer custody.
- `/prices` returns effective offers through the current date in Tawi-Tawi
  (UTC+8), excluding prices scheduled for a future date.
- The supplier dashboard reads PHP sales from `payment_recorded` payloads
  containing a positive `amount_php` or `amount`.

### Shipment compatibility

The current mobile app publishes one `note_added` event per selected batch.
The payload contains `shipment_id` (UUID), `destination`,
`shipment_batch_ids` (unique UUIDs), and `shipment_weight_kg`. The backend
checks that the supplier holds all selected batches, verifies the combined
weight, and prevents a shipment reference being reused with different contents.
These immutable notes are anchored just like other custody events and can be
read through `GET /batches/{id}/events`. A manifest reference records grouping;
it does not by itself transfer custody or declare a physical export. Individual
note requests remain idempotently retryable if publishing a manifest is interrupted.

### Reliable blockchain recovery

Immediate anchoring still uses background tasks. Committed `pending` rows also
act as a durable outbox, so a separate worker can recover writes interrupted by
an API restart or serverless request termination:

```bash
# Persistent worker, including retries of failed events:
python -m app.workers.chain_anchors --retry-failed

# One sweep for an external scheduler/cron:
python -m app.workers.chain_anchors --once --retry-failed --limit 50
```

Run this worker with the same database and Web3 environment as the API. It is
separate from the web request process; a serverless deployment needs an external
worker or scheduled job. Wallet operations are serialized, nonces include pending
transactions, and a reverted receipt is never marked anchored. If an event
already exists on-chain with the expected hash, recovery marks it anchored
without submitting a duplicate transaction. Transaction/block metadata can be
null in that recovery case; live verification remains available.

The existing HarvestLedger ABI and hash format are compatible with these
changes. No contract redeployment or database migration is required for this update.

## Local development

```bash
cp .env.example .env
docker compose up -d db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Interactive API docs: http://localhost:8000/docs
