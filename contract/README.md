# HarvestLedger

Solidity contract + Hardhat project for anchoring Agal's chain-of-custody
events on Sepolia. Farmers and suppliers never call this contract directly
-- only the FastAPI backend's service wallet does, via `web3.py`.

## What's on-chain, and why

Per event, `recordEvent(eventId, batchId, dataHash)` stores `{batchId,
dataHash, recordedAt}` keyed by `eventId`, and emits `EventRecorded` with
`batchId` indexed. No plaintext farmer/business data is ever stored on
chain -- `dataHash` is a `keccak256` digest computed off-chain by the
backend over the event's meaningful fields (event id, batch id, event
type, actor, occurred_at, and a hash of the JSON payload). Verifying a
batch's history means: fetch its events from the API, recompute the same
hash client-side, and confirm it matches what's anchored here. `batchId`
being an indexed event topic means anyone can pull "every on-chain record
for batch X" straight from logs via `eth_getLogs`, without the contract
needing to maintain an on-chain per-batch array (which would cost far more
gas as a batch accumulates events).

`eventId` and `batchId` are the custody event's and batch's
client-generated UUIDs, packed into `bytes32` (see `uuidToBytes32` in
`test/HarvestLedger.test.js` for the packing scheme the backend's
`web3.py` integration will mirror).

Access control is a single owner-managed allowlist
(`authorizedRecorders`) rather than a single hardcoded address, so the
backend's service wallet can be rotated by calling `setRecorder` without
redeploying.

## Setup

```bash
npm install
cp .env.example .env   # fill in SEPOLIA_RPC_URL and DEPLOYER_PRIVATE_KEY
npx hardhat test
npx hardhat run scripts/deploy.js --network sepolia
```

The deploy script prints the deployed address and, if
`SERVICE_WALLET_ADDRESS` is set in `.env` and differs from the deployer,
authorizes it as a recorder in the same run. Put the printed address into
`backend/.env` as `HARVEST_LEDGER_ADDRESS`.
