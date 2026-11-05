import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import {
  documentationGuides,
  storyChapters,
  storyHeroPhoto,
  type StoryPhoto,
} from "@/lib/documentation";

const description = "Discover the story behind Agal: regional mentoring, a regional championship, field interviews with traders and farmers, and the journey to the Quezon City semifinals. Explore photos and platform documentation.";

export const metadata: Metadata = {
  title: "Documentation & Our Story",
  description,
  openGraph: {
    title: "Documentation & Our Story · Agal",
    description,
    url: "/documentation",
    images: [{
      url: "/documentation/farmer-team-large.webp",
      width: 1600,
      height: 1200,
      alt: storyHeroPhoto.alt,
    }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Documentation & Our Story · Agal",
    description,
    images: ["/documentation/farmer-team-large.webp"],
  },
};

function StoryPhotograph({ photo, featured = false }: { photo: StoryPhoto; featured?: boolean }) {
  return (
    <figure className="overflow-hidden rounded-2xl border border-black/[.08] bg-surface dark:border-white/[.145]">
      <a
        href={`/documentation/${photo.id}-large.webp`}
        target="_blank"
        rel="noopener noreferrer"
        className="group relative block focus-visible:-outline-offset-4"
      >
        <Image
          src={`/documentation/${photo.id}.webp`}
          alt={photo.alt}
          width={photo.width}
          height={photo.height}
          sizes="(max-width: 639px) calc(100vw - 48px), (max-width: 1023px) calc(50vw - 36px), 476px"
          preload={featured}
          className="h-auto w-full"
        />
        <span aria-hidden="true" className="absolute right-3 bottom-3 flex h-8 w-8 items-center justify-center rounded-full bg-black/65 text-sm text-white transition-colors group-hover:bg-black/85">↗</span>
        <span className="sr-only">Open larger photo (opens in a new tab)</span>
      </a>
      <figcaption className="px-4 py-3 text-xs leading-6 text-zinc-600 dark:text-zinc-400">
        {photo.caption}
      </figcaption>
    </figure>
  );
}

export default function DocumentationPage() {
  return (
    <main id="story-top" className="mx-auto w-full max-w-5xl flex-1 px-6 py-12 sm:py-16">
      <header className="grid items-center gap-8 lg:grid-cols-2 lg:gap-12">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">Documentation &amp; our story</p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
            Rooted in <span className="whitespace-nowrap">Tawi-Tawi.</span><br />
            <span className="text-accent">Growing with every step.</span>
          </h1>
          <p className="mt-5 text-lg leading-8 text-zinc-600 dark:text-zinc-400">
            Behind Agal is a journey of mentoring, a regional championship,
            and conversations with the people in the seaweed supply chain.
            This is the story so far, told through the team&apos;s photographs.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <a href="#our-journey" className="rounded-full bg-accent px-5 py-3 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90">Follow our journey ↓</a>
            <a href="#platform-documentation" className="rounded-full border border-black/[.12] px-5 py-3 text-sm font-medium transition-colors hover:bg-surface dark:border-white/20">Explore the documentation</a>
          </div>
        </div>
        <StoryPhotograph photo={storyHeroPhoto} featured />
      </header>

      <section aria-labelledby="why-agal" className="mt-12 grid gap-5 rounded-2xl border border-accent/20 bg-accent/5 p-6 sm:mt-16 sm:p-8 md:grid-cols-[1fr_2fr] md:gap-10">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">The purpose behind the project</p>
          <h2 id="why-agal" className="mt-3 text-2xl font-semibold tracking-tight">Why Agal?</h2>
        </div>
        <div>
          <p className="leading-7 text-zinc-600 dark:text-zinc-400">
            Seaweed moves from farmers through traders and suppliers to buyers and
            exporters. Price information and the story of a harvest can become
            harder to follow along the way. Agal&apos;s goal is to make those
            connections clearer through transparent buying-price information and
            traceable harvest records.
          </p>
          <Link href="/overview" className="mt-4 inline-block text-sm font-medium text-accent underline underline-offset-4">Read the project overview →</Link>
        </div>
      </section>

      <section id="our-journey" aria-labelledby="journey-heading" className="scroll-mt-28 pt-14 sm:pt-16">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">The journey so far</p>
            <h2 id="journey-heading" className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">Five chapters. One shared purpose.</h2>
          </div>
          <a href="#quezon-city-semifinals" className="text-sm font-medium text-accent underline underline-offset-4">Jump to the latest chapter ↗</a>
        </div>
        <nav aria-label="Story chapters" className="mt-7">
          <ol className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {storyChapters.map((chapter) => (
              <li key={chapter.id}>
                <a href={`#${chapter.id}`} className="flex h-full items-center gap-3 rounded-xl border border-black/[.08] bg-surface px-4 py-4 transition-colors hover:border-accent dark:border-white/[.145] lg:flex-col lg:items-start">
                  <span className="text-sm font-semibold text-accent">{chapter.number}</span>
                  <span className="text-sm font-medium">{chapter.label}</span>
                  {chapter.status === "Ongoing" && <span className="ml-auto text-xs font-medium text-accent lg:ml-0">Ongoing</span>}
                </a>
              </li>
            ))}
          </ol>
        </nav>
        <p className="mt-4 text-xs leading-6 text-zinc-500 dark:text-zinc-400">Photographs from the team&apos;s project archive. Select a photo to open a larger version in a new tab.</p>

        {storyChapters.map((chapter) => (
          <section key={chapter.id} id={chapter.id} aria-labelledby={`${chapter.id}-heading`} className="scroll-mt-28 border-b border-black/[.08] py-12 sm:py-16 dark:border-white/[.145]">
            <div className={chapter.status === "Ongoing" ? "rounded-2xl border border-accent/25 bg-accent/5 p-6 sm:p-9" : ""}>
              <div className="grid gap-4 sm:grid-cols-[4rem_1fr] sm:gap-6">
                <span aria-hidden="true" className="text-4xl font-semibold tracking-tight text-accent/50 sm:text-5xl">{chapter.number}</span>
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">{chapter.label}</p>
                    {chapter.status === "Ongoing" && <span className="rounded-full border border-accent/30 px-3 py-1 text-xs font-semibold text-accent">Ongoing journey</span>}
                  </div>
                  <h3 id={`${chapter.id}-heading`} className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">{chapter.title}</h3>
                  <p className="mt-3 text-lg leading-8 text-zinc-700 dark:text-zinc-300">{chapter.summary}</p>
                  <div className="mt-4 max-w-3xl space-y-3 text-sm leading-7 text-zinc-600 dark:text-zinc-400">
                    {chapter.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
                  </div>
                </div>
              </div>
              {chapter.photos.length > 0 && (
                <div className="mt-7 grid items-start gap-5 sm:grid-cols-2 sm:gap-6">
                  {chapter.photos.map((photo) => <StoryPhotograph key={photo.id} photo={photo} />)}
                </div>
              )}
              {chapter.status === "Ongoing" && (
                <div className="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-accent/20 pt-5 text-sm font-medium text-accent">
                  <span>Tawi-Tawi</span><span aria-hidden="true">→</span><span>Quezon City</span>
                  <span className="w-full text-xs font-normal text-zinc-600 dark:text-zinc-400">Destination: the semifinals. The next chapter is still being written.</span>
                </div>
              )}
            </div>
          </section>
        ))}
      </section>

      <section id="platform-documentation" aria-labelledby="documentation-heading" className="scroll-mt-28 py-12 sm:py-16">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">From the story to the platform</p>
        <h2 id="documentation-heading" className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">Explore Agal&apos;s documentation</h2>
        <p className="mt-4 max-w-2xl leading-7 text-zinc-600 dark:text-zinc-400">One app connects three roles: farmers, suppliers and aggregators, and buyers and exporters. Here is where to learn what each part does.</p>
        <dl className="mt-7 grid gap-6 border-y border-black/[.08] py-7 sm:grid-cols-3 dark:border-white/[.145]">
          <div>
            <dt className="text-sm font-semibold">Mobile app</dt>
            <dd className="mt-2 text-sm leading-7 text-zinc-600 dark:text-zinc-400">Farmers can record harvests offline after signing in online, then synchronize when connected. Supplier and buyer workflows use an internet connection.</dd>
          </div>
          <div>
            <dt className="text-sm font-semibold">Backend &amp; shared records</dt>
            <dd className="mt-2 text-sm leading-7 text-zinc-600 dark:text-zinc-400">The API and database bring together price information, harvest events, and custody records across the app&apos;s roles.</dd>
          </div>
          <div>
            <dt className="text-sm font-semibold">Blockchain ledger</dt>
            <dd className="mt-2 text-sm leading-7 text-zinc-600 dark:text-zinc-400">Event fingerprints are anchored on a public ledger. A matching fingerprint verifies recorded data against its anchor; it does not inspect the physical harvest.</dd>
          </div>
        </dl>
        <div className="mt-7 grid gap-4 sm:grid-cols-3">
          {documentationGuides.map((guide) => (
            <Link key={guide.href} href={guide.href} className="group flex flex-col rounded-2xl border border-black/[.08] bg-surface p-6 transition-colors hover:border-accent dark:border-white/[.145]">
              <p className="text-xs font-medium text-accent">{guide.label}</p>
              <h3 className="mt-3 text-lg font-semibold tracking-tight">{guide.title}</h3>
              <p className="mt-3 flex-1 text-sm leading-7 text-zinc-600 dark:text-zinc-400">{guide.description}</p>
              <span aria-hidden="true" className="mt-5 text-accent">Explore →</span>
            </Link>
          ))}
        </div>
      </section>

      <section aria-labelledby="story-team-heading" className="rounded-2xl bg-[#002d26] p-7 text-white sm:p-9">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#83f5ce]">The people behind the journey</p>
        <h2 id="story-team-heading" className="mt-3 text-2xl font-semibold tracking-tight">Built together, for Tawi-Tawi.</h2>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-emerald-100/85">Student developers Junrey Gonzales, Krishane Ann Remonde, and Moh. Hamsya Igasan, with mentor Ramat Hailaya. Agal is built for the Philippine Startup Challenge.</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/#developers-heading" className="rounded-full border border-white/30 px-5 py-3 text-sm font-medium transition-colors hover:bg-white/10">Meet the developers</Link>
          <Link href="/#download" className="rounded-full bg-[#83f5ce] px-5 py-3 text-sm font-semibold text-[#002d26] transition-opacity hover:opacity-90">Explore the app</Link>
        </div>
      </section>
      <a href="#story-top" className="mt-8 inline-block text-sm font-medium text-accent underline underline-offset-4">Back to the beginning ↑</a>
    </main>
  );
}
