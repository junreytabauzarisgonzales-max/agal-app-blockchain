import Link from "next/link";

export default function OverviewPage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-12 px-6 py-16">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">Project overview</h1>
        <p className="mt-3 text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          Agal is a price-transparency and traceability platform for the seaweed
          supply chain in Tawi-Tawi, Philippines &mdash; built for the Philippine
          Startup Challenge.
        </p>
      </header>

      <section className="flex flex-col gap-3">
        <h2 className="text-xl font-semibold">The problem</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Seaweed farmers in Tawi-Tawi often have little visibility into fair
          market prices and little ability to prove where their harvest went
          once it leaves their hands. That makes it hard to negotiate fairly and
          hard for buyers and exporters to verify the origin and handling of
          what they&apos;re purchasing.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-xl font-semibold">How Agal works</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          One mobile app serves three roles &mdash; Farmer, Supplier/Aggregator,
          and Buyer/Exporter &mdash; each with the experience that role actually
          needs.
        </p>
        <ul className="list-disc space-y-2 pl-5 leading-7 text-zinc-600 dark:text-zinc-400">
          <li>
            <strong className="text-zinc-950 dark:text-zinc-50">Farmers</strong> log
            harvests and handoffs fully offline; everything syncs automatically
            once a connection is available, and nothing is ever lost or
            overwritten.
          </li>
          <li>
            <strong className="text-zinc-950 dark:text-zinc-50">
              Suppliers/Aggregators
            </strong>{" "}
            see incoming batches, confirm receipt, and post transparent prices.
          </li>
          <li>
            <strong className="text-zinc-950 dark:text-zinc-50">
              Buyers/Exporters
            </strong>{" "}
            verify a batch&apos;s full history before purchasing and record the
            transaction.
          </li>
        </ul>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-xl font-semibold">A tamper-evident chain of custody</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Every step a batch takes &mdash; harvested, dried, transferred, sold,
          exported &mdash; is recorded as an event and hashed onto a public
          blockchain ledger. No farm or business data is ever stored on-chain,
          only a cryptographic fingerprint of each event, so anyone can
          independently confirm a batch&apos;s recorded history hasn&apos;t been
          altered after the fact.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-xl font-semibold">Why Tawi-Tawi</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Tawi-Tawi is one of the Philippines&apos; major seaweed-farming provinces,
          with a supply chain that runs through many small-scale farmers before
          reaching aggregators and exporters. That length and fragmentation is
          exactly where price information gets lost and where it becomes hard to
          trace a shipment back to how &mdash; and by whom &mdash; it was actually
          produced.
        </p>
      </section>

      <section className="border-t border-black/[.08] pt-8 dark:border-white/[.145]">
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Want the technical details?{" "}
          <Link href="/how-it-works" className="font-medium text-foreground underline">
            See how it works
          </Link>
          , walk through the{" "}
          <Link href="/manual" className="font-medium text-foreground underline">
            user manual
          </Link>
          , or check the{" "}
          <Link href="/faq" className="font-medium text-foreground underline">
            FAQ
          </Link>
          .
        </p>
      </section>
    </main>
  );
}
