import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { newsPosts } from "@/lib/news";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

type Params = Promise<{ slug: string }>;

export function generateStaticParams() {
  return newsPosts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: { params: Params }): Promise<Metadata> {
  const { slug } = await params;
  const post = newsPosts.find((p) => p.slug === slug);
  return { title: post?.title ?? "News" };
}

export default async function NewsPostPage({ params }: { params: Params }) {
  const { slug } = await params;
  const post = newsPosts.find((p) => p.slug === slug);
  if (!post) notFound();

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <Link href="/news" className="text-sm font-medium text-zinc-500 hover:text-foreground">
        &larr; Back to news
      </Link>
      <header>
        <time dateTime={post.date} className="text-sm text-zinc-500">
          {formatDate(post.date)}
        </time>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">{post.title}</h1>
      </header>
      <div className="flex flex-col gap-4">
        {post.body.map((paragraph, index) => (
          <p key={index} className="leading-7 text-zinc-600 dark:text-zinc-400">
            {paragraph}
          </p>
        ))}
      </div>
    </main>
  );
}
