"use client";

import { useState } from "react";
import { SEPOLIA_CONTRACT_ADDRESS, SEPOLIA_CONTRACT_URL } from "@/lib/config";
import { CopyIcon, ExternalLinkIcon } from "@/components/Icons";

export default function ContractCard() {
  const [copyStatus, setCopyStatus] = useState("");

  async function copyAddress() {
    try {
      await navigator.clipboard.writeText(SEPOLIA_CONTRACT_ADDRESS);
      setCopyStatus("Contract address copied.");
    } catch {
      setCopyStatus("Copy unavailable. Select and copy the full address below.");
    }
  }

  return (
    <article className="flex flex-col rounded-2xl border border-black/[.08] bg-surface p-6 dark:border-white/[.145]">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="font-semibold">AGAL Smart Contract</h3>
        <span className="rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent">Sepolia Testnet</span>
      </div>
      <p className="mt-3 text-sm leading-6 text-zinc-600 dark:text-zinc-400">Explore the public contract used to anchor Agal&apos;s chain-of-custody records.</p>
      <div className="mt-4 flex items-center gap-3">
        <span aria-hidden="true" className="font-mono text-lg font-medium">{SEPOLIA_CONTRACT_ADDRESS.slice(0, 6)}…{SEPOLIA_CONTRACT_ADDRESS.slice(-4)}</span>
        <button type="button" onClick={copyAddress} aria-label="Copy AGAL contract address" className="inline-flex min-h-10 items-center gap-2 rounded-full border border-black/10 px-3 text-xs font-medium transition-colors hover:border-accent hover:text-accent dark:border-white/20">
          <CopyIcon /> Copy
        </button>
      </div>
      <p className="mt-3 break-all font-mono text-xs leading-6 text-zinc-600 dark:text-zinc-400" aria-label="Full contract address">{SEPOLIA_CONTRACT_ADDRESS}</p>
      <a href={SEPOLIA_CONTRACT_URL} target="_blank" rel="noopener noreferrer" className="mt-4 inline-flex min-h-10 w-fit items-center gap-2 text-sm font-medium text-accent underline underline-offset-4">
        View on Etherscan <ExternalLinkIcon /><span className="sr-only"> (opens in a new tab)</span>
      </a>
      <p role="status" className="mt-3 min-h-5 text-xs text-zinc-600 dark:text-zinc-400">{copyStatus}</p>
    </article>
  );
}
