import Link from "next/link";
import { newsPosts } from "@/lib/news";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default function NewsPage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-10 px-6 py-16">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">News &amp; updates</h1>
        <p className="mt-3 text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          What&apos;s new with Agal.
        </p>
      </header>

      <ul className="flex flex-col gap-10">
        {newsPosts.map((post) => (
          <li key={post.slug} className="border-t border-black/[.08] pt-8 dark:border-white/[.145]">
            <time dateTime={post.date} className="text-sm text-zinc-500">
              {formatDate(post.date)}
            </time>
            <h2 className="mt-2 text-xl font-semibold">
              <Link href={`/news/${post.slug}`} className="hover:underline">
                {post.title}
              </Link>
            </h2>
            <p className="mt-3 leading-7 text-zinc-600 dark:text-zinc-400">{post.summary}</p>
            <Link
              href={`/news/${post.slug}`}
              className="mt-3 inline-block text-sm font-medium text-foreground underline"
            >
              Read more &rarr;
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
