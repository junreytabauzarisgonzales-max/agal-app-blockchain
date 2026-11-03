import type { Metadata } from "next";
import Link from "next/link";
import TutorialStep from "@/components/TutorialStep";
import { tutorialGuides, tutorialQuestions } from "@/lib/tutorial";

export const metadata: Metadata = {
  title: "App Tutorial",
  description: "Learn to use Agal with step-by-step app screenshots: log harvests offline, check buying prices, use SMS, bundle shipments, and verify batch provenance.",
};

export default function TutorialPage() {
  return (
    <main id="tutorial-top" className="mx-auto w-full max-w-5xl flex-1 px-6 py-12 sm:py-16">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">The visual app guide</p>
        <h1 className="mt-4 max-w-2xl text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">Agal, step by step.</h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          Follow the screenshots to log your first harvest, connect with trading partners,
          manage shipments, and check a batch&apos;s journey. Start with the role you use in the app.
        </p>
        <nav aria-label="Choose a tutorial" className="mt-8 grid gap-3 sm:grid-cols-3">
          {tutorialGuides.map((guide) => (
            <a key={guide.id} href={`#${guide.id}`} className="group flex items-center gap-4 rounded-2xl border border-black/[.08] bg-surface p-5 transition-colors hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent dark:border-white/[.145]">
              <span className="text-2xl font-semibold text-accent/60">{guide.number}</span>
              <span className="flex-1">
                <span className="block text-sm font-semibold">{guide.role}</span>
                <span className="mt-1 block text-xs text-zinc-500">{guide.steps.length} screenshot walkthroughs</span>
              </span>
              <span aria-hidden="true" className="text-accent transition-transform group-hover:translate-y-1 motion-reduce:transform-none">↓</span>
            </a>
          ))}
        </nav>
        <p className="mt-5 text-xs leading-6 text-zinc-500 dark:text-zinc-400">
          Screenshots show demonstration accounts and sample records, prices, payments, and verification results.
          Your account details and live data will be different. Select any screenshot to open a larger version.
        </p>
      </header>

      <section aria-labelledby="getting-started" className="mt-12 rounded-2xl border border-accent/20 bg-accent/5 p-6 sm:p-8">
        <h2 id="getting-started" className="text-xl font-semibold">Before you begin</h2>
        <ol className="mt-5 grid gap-6 sm:grid-cols-3">
          <li>
            <p className="text-sm font-semibold"><span className="mr-2 text-accent">1.</span> Open the app</p>
            <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">Use the <Link href="/#download" className="font-medium text-accent underline underline-offset-4">download section</Link> to check availability, then open Agal on your device.</p>
          </li>
          <li>
            <p className="text-sm font-semibold"><span className="mr-2 text-accent">2.</span> Sign in to your role</p>
            <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">Connect to the internet, select Farmer, Supplier, or Buyer, and sign in with your account&apos;s email and password.</p>
          </li>
          <li>
            <p className="text-sm font-semibold"><span className="mr-2 text-accent">3.</span> Find your way around</p>
            <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">Use Home, Batches, Messages, and Profile in the bottom navigation. Settings and account options are inside Profile.</p>
          </li>
        </ol>
      </section>

      {tutorialGuides.map((guide) => (
        <section key={guide.id} id={guide.id} aria-labelledby={`${guide.id}-heading`} className="scroll-mt-24 border-b border-black/[.08] py-14 sm:py-16 dark:border-white/[.145]">
          <div className="flex flex-wrap items-center gap-3">
            <span className="rounded-full bg-accent px-3 py-1 text-xs font-semibold text-accent-foreground">{guide.number} / {guide.role}</span>
            <span className="text-xs text-zinc-500 dark:text-zinc-400">Example account: {guide.account}</span>
          </div>
          <h2 id={`${guide.id}-heading`} className="mt-5 text-2xl font-semibold tracking-tight sm:text-3xl">{guide.title}</h2>
          <p className="mt-3 max-w-2xl text-base leading-7 text-zinc-600 dark:text-zinc-400">{guide.summary}</p>
          <p className="mt-3 text-xs font-medium text-accent">{guide.connectivity}</p>
          <nav aria-label={`${guide.role} tutorial steps`} className="mt-6 flex flex-wrap gap-x-5 gap-y-3 text-xs">
            {guide.steps.map((step, index) => (
              <a key={step.id} href={`#${step.id}`} className="text-zinc-600 underline decoration-black/15 underline-offset-4 hover:text-accent dark:text-zinc-400 dark:decoration-white/20">
                {index + 1}. {step.title}
              </a>
            ))}
          </nav>
          <div className="mt-8 grid items-start gap-6 md:grid-cols-2">
            {guide.steps.map((step, index) => <TutorialStep key={step.id} step={step} number={index + 1} />)}
          </div>
          <a href="#tutorial-top" className="mt-7 inline-block text-xs font-medium text-accent underline underline-offset-4">Back to role selection ↑</a>
        </section>
      ))}

      <section aria-labelledby="tutorial-help" className="py-12 sm:py-16">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">A little extra help</p>
        <h2 id="tutorial-help" className="mt-3 text-2xl font-semibold tracking-tight">Questions while using the app?</h2>
        <div className="mt-6 divide-y divide-black/[.08] rounded-2xl border border-black/[.08] px-5 dark:divide-white/[.145] dark:border-white/[.145] sm:px-7">
          {tutorialQuestions.map((item) => (
            <details key={item.question} className="group py-5">
              <summary className="flex cursor-pointer list-none items-start justify-between gap-4 text-sm font-semibold">
                {item.question}<span aria-hidden="true" className="text-accent group-open:hidden">+</span><span aria-hidden="true" className="hidden text-accent group-open:block">−</span>
              </summary>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-zinc-600 dark:text-zinc-400">{item.answer}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="flex flex-col items-start gap-5 rounded-2xl bg-[#002d26] p-7 text-white sm:flex-row sm:items-center sm:justify-between sm:p-9">
        <div>
          <h2 className="text-xl font-semibold">Ready to log your first harvest?</h2>
          <p className="mt-2 max-w-lg text-sm leading-6 text-emerald-100/80">Keep this guide handy as you explore Agal. The user manual has a quick role-by-role reference, too.</p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-3">
          <Link href="/manual" className="rounded-full border border-white/30 px-5 py-3 text-sm font-medium transition-colors hover:bg-white/10">User manual</Link>
          <Link href="/#download" className="rounded-full bg-[#83f5ce] px-5 py-3 text-sm font-semibold text-[#002d26] transition-opacity hover:opacity-90">Get the app</Link>
        </div>
      </section>
    </main>
  );
}
