import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Terms of Use" };

export default function TermsPage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">Terms of use</h1>
        <p className="mt-3 text-sm text-zinc-500">
          Draft &mdash; last updated September 2026. This is a working draft for the
          Philippine Startup Challenge and has not yet been reviewed by legal counsel.
        </p>
      </header>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">1. Acceptance of these terms</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          By creating an account or using the Agal mobile app or website (together,
          the &ldquo;Service&rdquo;), you agree to these Terms of Use. If you do not
          agree, please do not use the Service.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">2. Who can use Agal</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Agal is intended for farmers, aggregators/suppliers, and buyers/exporters
          participating in the seaweed supply chain. You are responsible for choosing
          the role that accurately describes you when you register, and for keeping
          your account credentials confidential.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">3. Accuracy of information you submit</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Harvest batch details, chain-of-custody events, and price records you enter
          are your responsibility. Agal does not independently verify weights, prices,
          or locations you submit &mdash; it records what you enter and makes that
          record tamper-evident, not necessarily accurate at the point of entry.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">4. Blockchain records are permanent</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          A cryptographic hash of each chain-of-custody event is anchored on a public
          blockchain ledger. Once anchored, that record cannot be edited or deleted by
          Agal or by you &mdash; that permanence is what makes the history verifiable.
          Do not submit anything you would not want permanently, verifiably recorded
          as having occurred at that time.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">5. Acceptable use</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          You agree not to use the Service to submit false chain-of-custody or price
          information, to interfere with the Service&apos;s operation, or to attempt to
          access accounts or data that are not yours.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">6. Service availability</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Agal is provided on an &ldquo;as is&rdquo; basis while under active
          development for the Philippine Startup Challenge. Features, availability,
          and these terms may change as the Service evolves.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">7. Contact</h2>
        <p className="leading-7 text-zinc-600 dark:text-zinc-400">
          Questions about these terms can be directed to the Agal team through the
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
