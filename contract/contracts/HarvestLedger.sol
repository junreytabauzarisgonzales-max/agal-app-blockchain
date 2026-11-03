// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title HarvestLedger
/// @notice Anchors a tamper-evident hash of every chain-of-custody event
/// recorded by the Agal backend, so a batch's full history (fetched from
/// the API) can be independently verified: refetch the event, recompute
/// the same hash client-side, and check it matches what's stored here.
///
/// No plaintext farmer/business data is ever stored on-chain -- only a
/// keccak256 digest per event, plus the minimum metadata (the batch it
/// belongs to) needed to discover "every on-chain record for batch X"
/// from event logs without an expensive on-chain array.
///
/// Farmers and suppliers never call this contract directly. Only the
/// backend's service wallet (an address in `authorizedRecorders`) does,
/// via web3.py, after a chain-of-custody event has already been durably
/// written to Postgres.
contract HarvestLedger {
    struct Record {
        bytes32 batchId;
        bytes32 dataHash;
        uint256 recordedAt;
        bool exists;
    }

    address public owner;
    mapping(address => bool) public authorizedRecorders;

    /// Keyed by eventId -- the chain-of-custody event's client-generated
    /// UUID, encoded as bytes32 (see off-chain encoding note below).
    mapping(bytes32 => Record) private records;

    event RecorderUpdated(address indexed recorder, bool authorized);

    /// `batchId` is indexed so anyone can query "every event recorded
    /// for this batch" via `eth_getLogs`, without the contract needing
    /// to maintain an on-chain per-batch array.
    event EventRecorded(bytes32 indexed eventId, bytes32 indexed batchId, bytes32 dataHash, uint256 recordedAt);

    error NotOwner();
    error NotAuthorized();
    error AlreadyRecorded(bytes32 eventId);
    error ZeroAddress();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlyAuthorized() {
        if (!authorizedRecorders[msg.sender]) revert NotAuthorized();
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedRecorders[msg.sender] = true;
        emit RecorderUpdated(msg.sender, true);
    }

    /// Grants or revokes permission to call `recordEvent`. Expected to be
    /// called once after deployment to authorize the backend's service
    /// wallet (if it differs from the deploying address), and again if
    /// that wallet is ever rotated.
    function setRecorder(address recorder, bool authorized) external onlyOwner {
        if (recorder == address(0)) revert ZeroAddress();
        authorizedRecorders[recorder] = authorized;
        emit RecorderUpdated(recorder, authorized);
    }

    /// Anchors one chain-of-custody event. Reverts if `eventId` was
    /// already recorded -- records are append-only, exactly like the
    /// Postgres rows they mirror.
    function recordEvent(bytes32 eventId, bytes32 batchId, bytes32 dataHash) external onlyAuthorized {
        if (records[eventId].exists) revert AlreadyRecorded(eventId);

        records[eventId] = Record({batchId: batchId, dataHash: dataHash, recordedAt: block.timestamp, exists: true});

        emit EventRecorded(eventId, batchId, dataHash, block.timestamp);
    }

    function getRecord(bytes32 eventId)
        external
        view
        returns (bytes32 batchId, bytes32 dataHash, uint256 recordedAt, bool exists)
    {
        Record storage r = records[eventId];
        return (r.batchId, r.dataHash, r.recordedAt, r.exists);
    }

    function isRecorded(bytes32 eventId) external view returns (bool) {
        return records[eventId].exists;
    }
}
