const hre = require('hardhat');

async function main() {
  const HarvestLedger = await hre.ethers.getContractFactory('HarvestLedger');
  const ledger = await HarvestLedger.deploy();
  await ledger.waitForDeployment();

  const address = await ledger.getAddress();
  console.log(`HarvestLedger deployed to: ${address}`);

  const serviceWallet = process.env.SERVICE_WALLET_ADDRESS;
  if (serviceWallet) {
    const [deployer] = await hre.ethers.getSigners();
    if (serviceWallet.toLowerCase() !== deployer.address.toLowerCase()) {
      console.log(`Authorizing service wallet ${serviceWallet} as a recorder...`);
      const tx = await ledger.setRecorder(serviceWallet, true);
      await tx.wait();
      console.log('Done.');
    }
  }

  console.log('\nSet this in backend/.env:');
  console.log(`HARVEST_LEDGER_ADDRESS=${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
