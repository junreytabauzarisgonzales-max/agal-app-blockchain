import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "How It Works" };

const pipeline = [
  {
    title: "Log it, even offline",
    detail:
      "A farmer records a harvest or a handoff on their phone. It's written straight to a local database on the device -- no connection required, and nothing is ever lost if the app closes or the signal drops.",
  },
  {
    title: "Sync when you can",
    detail:
      "The app pushes queued records to the Agal server as soon as a connection is available, in the background. Every record carries an id generated on the device, so replaying the same sync twice is harmless -- the server just recognizes it's already there.",
  },
  {
    title: "Recorded as history, not a snapshot",
    detail:
      "Nothing about a batch is ever overwritten. Every step -- harvested, drying, dried, handed to a supplier, sold, exported -- is stored as its own permanent entry. A batch's current status is simply the latest entry in that history, so the full sequence of what happened is always there to inspect.",
  },
  {
    title: "Hashed and anchored on-chain",
    detail:
      "The server computes a cryptographic fingerprint (a keccak256 hash) of each event and submits it to a smart contract on a public blockchain. Only that fingerprint goes on-chain -- never the farmer's name, the price, or any other plaintext detail.",
  },
  {
    title: "Verifiable by anyone",
    detail:
      "Because the fingerprint is public and the event that produced it can be re-fetched from Agal, anyone -- a buyer, an exporter, an auditor -- can recompute the same hash and confirm it matches what's on-chain. If a record were ever altered after the fact, the hashes would no longer match.",
  },
];

const stack = [
  { layer: "Mobile app", detail: "Flutter, with an on-device database for the offline-first Farmer experience." },
  { layer: "Backend", detail: "A REST API backed by PostgreSQL, storing every chain-of-custody event as an immutable record." },
  { layer: "Ledger", detail: "A smart contract on a public Ethereum test network, anchoring one hash per event." },
];

export default function HowItWorksPage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-12 px-6 py-16">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">How it works</h1>
        <p className="mt-3 text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          From a farmer&apos;s phone at the water&apos;s edge to a permanent, verifiable
          record. Here&apos;s the full path a single harvest takes through Agal.
        </p>
      </header>

      <section>
        <ol className="flex flex-col gap-8">
          {pipeline.map((step, index) => (
            <li key={step.title} className="flex gap-5">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-semibold text-accent-foreground">
                {index + 1}
              </span>
              <div>
                <h2 className="font-semibold">{step.title}</h2>
                <p className="mt-1 leading-7 text-zinc-600 dark:text-zinc-400">{step.detail}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="rounded-2xl border border-black/[.08] bg-surface p-8 dark:border-white/[.145]">
        <h2 className="text-lg font-semibold">Under the hood</h2>
        <dl className="mt-6 flex flex-col gap-4">
          {stack.map((item) => (
            <div key={item.layer} className="grid gap-1 sm:grid-cols-[140px_1fr] sm:gap-4">
              <dt className="text-sm font-medium text-zinc-500">{item.layer}</dt>
              <dd className="text-sm leading-6 text-zinc-700 dark:text-zinc-300">{item.detail}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Curious what this looks like day-to-day for each role?{" "}
          <Link href="/manual" className="font-medium text-foreground underline">
            Read the user manual
          </Link>
          , or go back to the{" "}
          <Link href="/overview" className="font-medium text-foreground underline">
            project overview
          </Link>
          .
        </p>
      </section>
    </main>
  );
}
