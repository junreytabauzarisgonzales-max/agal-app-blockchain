const { expect } = require('chai');
const { ethers } = require('hardhat');

/** Packs a UUID string (36 chars, with dashes) into a bytes32 for use as a mapping key. */
function uuidToBytes32(uuid) {
  const hex = uuid.replace(/-/g, '');
  return ethers.zeroPadValue('0x' + hex, 32);
}

function hashOf(text) {
  return ethers.keccak256(ethers.toUtf8Bytes(text));
}

describe('HarvestLedger', () => {
  async function deployFixture() {
    const [owner, otherRecorder, stranger] = await ethers.getSigners();
    const HarvestLedger = await ethers.getContractFactory('HarvestLedger');
    const ledger = await HarvestLedger.deploy();
    await ledger.waitForDeployment();
    return { ledger, owner, otherRecorder, stranger };
  }

  const eventId = uuidToBytes32('a87f4647-ace8-4de6-96f0-34a98c4cba5d');
  const batchId = uuidToBytes32('9be0499f-4e49-4ec8-ad64-f17da9dc8dff');
  const dataHash = hashOf('drying_started@2026-09-15T09:00:00Z');

  it('authorizes the deployer as a recorder on construction', async () => {
    const { ledger, owner } = await deployFixture();
    expect(await ledger.owner()).to.equal(owner.address);
    expect(await ledger.authorizedRecorders(owner.address)).to.equal(true);
  });

  it('records an event and makes it queryable', async () => {
    const { ledger, owner } = await deployFixture();

    await expect(ledger.recordEvent(eventId, batchId, dataHash))
      .to.emit(ledger, 'EventRecorded')
      .withArgs(eventId, batchId, dataHash, (ts) => ts > 0n);

    const record = await ledger.getRecord(eventId);
    expect(record.batchId).to.equal(batchId);
    expect(record.dataHash).to.equal(dataHash);
    expect(record.exists).to.equal(true);
    expect(await ledger.isRecorded(eventId)).to.equal(true);
  });

  it('rejects recording the same eventId twice', async () => {
    const { ledger } = await deployFixture();
    await ledger.recordEvent(eventId, batchId, dataHash);

    await expect(ledger.recordEvent(eventId, batchId, dataHash))
      .to.be.revertedWithCustomError(ledger, 'AlreadyRecorded')
      .withArgs(eventId);
  });

  it('rejects recordEvent from an unauthorized address', async () => {
    const { ledger, stranger } = await deployFixture();

    await expect(ledger.connect(stranger).recordEvent(eventId, batchId, dataHash)).to.be.revertedWithCustomError(
      ledger,
      'NotAuthorized',
    );
  });

  it('lets the owner authorize a new recorder, who can then record events', async () => {
    const { ledger, otherRecorder } = await deployFixture();

    await expect(ledger.setRecorder(otherRecorder.address, true))
      .to.emit(ledger, 'RecorderUpdated')
      .withArgs(otherRecorder.address, true);

    await expect(ledger.connect(otherRecorder).recordEvent(eventId, batchId, dataHash)).to.not.be.reverted;
  });

  it('rejects setRecorder from a non-owner', async () => {
    const { ledger, stranger, otherRecorder } = await deployFixture();

    await expect(ledger.connect(stranger).setRecorder(otherRecorder.address, true)).to.be.revertedWithCustomError(
      ledger,
      'NotOwner',
    );
  });

  it('rejects setRecorder(address(0), ...)', async () => {
    const { ledger } = await deployFixture();

    await expect(ledger.setRecorder(ethers.ZeroAddress, true)).to.be.revertedWithCustomError(ledger, 'ZeroAddress');
  });
});
