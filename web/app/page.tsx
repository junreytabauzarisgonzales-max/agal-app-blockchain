import Link from "next/link";
import Image from "next/image";
import ApiHealthCard from "@/components/ApiHealthCard";
import ContractCard from "@/components/ContractCard";
import DevelopersSection from "@/components/DevelopersSection";
import DownloadCard from "@/components/DownloadCard";
import FaqList from "@/components/FaqList";
import RoleCard from "@/components/RoleCard";
import { faqs } from "@/lib/faq";
import { SITE_TAGLINE } from "@/lib/config";

const pipelinePreview = [
  "Log a harvest or handoff on your phone -- offline is fine.",
  "It syncs to Agal automatically once you have a connection.",
  "Each step is hashed and anchored on a public blockchain ledger.",
  "Anyone can verify the batch's history hasn't been altered.",
];

export default function Home() {
  return (
    <main className="flex w-full flex-1 flex-col">
      <section className="relative isolate mx-auto flex w-full max-w-5xl flex-col gap-6 overflow-hidden px-6 py-20 sm:py-28">
        <input type="checkbox" id="hero-motion" className="hero-motion-toggle sr-only" aria-label="Pause decorative logo animation" />
        <div aria-hidden="true" className="hero-artwork">
          <Image src="/branding/agal-hero.webp" alt="" width={708} height={709} sizes="(max-width: 640px) 80vw, 544px" className="h-auto w-full" />
        </div>
        <label htmlFor="hero-motion" className="hero-motion-label absolute right-6 bottom-5 cursor-pointer rounded-full border border-black/10 bg-background/80 px-3 py-2 text-xs text-zinc-600 dark:border-white/15 dark:text-zinc-400">
          <span className="motion-pause">Pause animation</span><span className="motion-resume">Resume animation</span>
        </label>
        <h1 className="max-w-2xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
          {SITE_TAGLINE}
        </h1>
        <p className="max-w-xl text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          Agal gives seaweed farmers, aggregators, and exporters in Tawi-Tawi a shared,
          tamper-evident record of every harvest &mdash; from the water to the buyer &mdash;
          along with transparent, up-to-date price information.
        </p>
        <div className="flex flex-wrap gap-3 text-sm text-zinc-600 dark:text-zinc-400">
          <span className="rounded-full border border-black/[.08] px-3 py-1 dark:border-white/[.145]">
            Works offline
          </span>
          <span className="rounded-full border border-black/[.08] px-3 py-1 dark:border-white/[.145]">
            Blockchain-verified history
          </span>
          <span className="rounded-full border border-black/[.08] px-3 py-1 dark:border-white/[.145]">
            One app, three roles
          </span>
        </div>
        <Link href="/tutorial" className="mt-2 inline-flex w-fit items-center gap-3 rounded-full bg-accent px-5 py-3 text-sm font-semibold text-accent-foreground transition-opacity hover:opacity-90">
          Learn to use the app <span aria-hidden="true">→</span>
        </Link>
      </section>

      <section aria-labelledby="platform-heading" className="mx-auto w-full max-w-5xl px-6 pb-16">
        <h2 id="platform-heading" className="text-xl font-semibold">Connected to a verifiable record</h2>
        <p className="mt-2 max-w-2xl text-sm leading-7 text-zinc-600 dark:text-zinc-400">Visit Agal&apos;s backend health endpoint and explore the deployed contract on Sepolia.</p>
        <div className="mt-6 grid gap-5 md:grid-cols-2">
          <ApiHealthCard />
          <ContractCard />
        </div>
      </section>

      <section className="border-t border-black/[.08] bg-surface dark:border-white/[.145]">
        <div className="mx-auto grid max-w-5xl gap-6 px-6 py-16 sm:grid-cols-3">
          <RoleCard
            title="Farmers"
            description="Log harvests and handoffs right from the water's edge, even with no signal. Everything syncs automatically once you're back online."
          />
          <RoleCard
            title="Suppliers & Aggregators"
            description="See incoming batches, confirm receipt, and post fair, transparent prices for the species you're buying."
          />
          <RoleCard
            title="Buyers & Exporters"
            description="Verify a batch's full chain of custody before you buy, and record purchases with confidence."
          />
        </div>
      </section>

      <section className="mx-auto w-full max-w-5xl px-6 py-16">
        <h2 className="text-xl font-semibold">From harvest to verified record</h2>
        <ol className="mt-6 flex flex-col gap-4">
          {pipelinePreview.map((step, index) => (
            <li key={step} className="flex gap-4">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent text-xs font-semibold text-accent-foreground">
                {index + 1}
              </span>
              <span className="leading-6 text-zinc-700 dark:text-zinc-300">{step}</span>
            </li>
          ))}
        </ol>
        <Link href="/how-it-works" className="mt-6 inline-block text-sm font-medium text-foreground underline">
          See the full pipeline &rarr;
        </Link>
      </section>

      <section className="border-t border-black/[.08] px-6 py-16 dark:border-white/[.145]">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-xl font-semibold">Frequently asked questions</h2>
          <div className="mt-6">
            <FaqList items={faqs.slice(0, 4)} />
          </div>
          <Link href="/faq" className="mt-6 inline-block text-sm font-medium text-foreground underline">
            See all FAQs &rarr;
          </Link>
        </div>
      </section>

      <section className="border-t border-black/[.08] px-6 py-16 dark:border-white/[.145]">
        <div className="mx-auto max-w-5xl">
          <DownloadCard />
        </div>
      </section>

      <section className="mx-auto w-full max-w-5xl px-6 py-16">
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Want the full picture?{" "}
          <Link href="/overview" className="font-medium text-foreground underline">
            Read the project overview
          </Link>
          , walk through the{" "}
          <Link href="/manual" className="font-medium text-foreground underline">
            user manual
          </Link>
          , or{" "}
          <Link href="/news" className="font-medium text-foreground underline">
            check the latest updates
          </Link>
          .
        </p>
      </section>
      <DevelopersSection />
    </main>
  );
}
