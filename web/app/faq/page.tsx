import type { Metadata } from "next";
import FaqList from "@/components/FaqList";
import { faqs } from "@/lib/faq";

export const metadata: Metadata = { title: "FAQ" };

export default function FaqPage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">Frequently asked questions</h1>
        <p className="mt-3 text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          Everything we get asked most about how Agal works.
        </p>
      </header>
      <FaqList items={faqs} />
    </main>
  );
}
