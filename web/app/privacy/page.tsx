import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Privacy Policy" };

export default function PrivacyPage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">Privacy policy</h1>
        <p className="mt-3 text-sm text-zinc-500">
          Draft &mdash; last updated September 2026. This is a working draft for the
          Philippine Startup Challenge and has not yet been reviewed by legal counsel.
        </p>
      </header>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">What we collect</h2>
        <ul className="list-disc space-y-2 pl-5 leading-7 text-zinc-600 dark:text-zinc-400">
          <li>
            <strong className="text-foreground">Account information:</strong> email
            address, full name, your chosen role (Farmer, Supplier/Aggregator, or
            Buyer/Exporter), and optionally a phone number and municipality.
          </li>
          <li>
            <strong className="text-foreground">Harvest and custody data:</strong>{" "}
            batch details (species, estimated weight, harvest location and date) and
            chain-of-custody events (drying, transfers, notes) that you or another
            role in the same supply chain records.
          </li>
          <li>
            <strong className="text-foreground">Messages:</strong> the content of
            chats you send to other Agal users, and who you sent them to.
          </li>
          <li>
            <strong className="text-foreground">Price data:</strong> prices posted by
            Suppliers/Aggregators and Buyers/Exporters, along with which account
            posted them.
          </li>
        </ul>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">What we don&apos;t collect</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Agal does not use third-party advertising trackers, and does not sell your
          data. The marketing website you&apos;re reading now has no login and doesn&apos;t
          collect personal information at all.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">What goes on the public blockchain</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Chain-of-custody events are anchored on a public blockchain ledger so their
          history can be independently verified. Only a cryptographic hash of each
          event is published on-chain &mdash; never your name, contact details, prices,
          messages, or the plain content of the event. Your account and batch data stay in
          Agal&apos;s own database; the blockchain only ever sees an opaque fingerprint of
          it.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">Who can see your data</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Batch and chain-of-custody information is visible to the roles involved in
          that batch&apos;s supply chain, since traceability is the point of the Service.
          Price data you post is visible to other Agal users so that pricing stays
          transparent. Messages are only visible to you and the person you&apos;re
          messaging. Your account credentials are never shared.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">Sending a message via SMS</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          If you choose to send a message via SMS instead of in-app, that message is
          handed off to your phone&apos;s own default messaging app &mdash; Agal does not
          see, store, or have access to anything sent that way.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">Data retention</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          We retain account and batch data for as long as your account is active.
          Chain-of-custody hashes anchored on the public blockchain cannot be deleted
          once recorded, as described in our{" "}
          <Link href="/terms" className="underline">
            Terms of Use
          </Link>
          .
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">Contact</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Questions about this policy can be directed to the Agal team through the
          channels announced on our{" "}
          <Link href="/news" className="underline">
            news page
          </Link>
          .
        </p>
      </section>
    </main>
  );
}
