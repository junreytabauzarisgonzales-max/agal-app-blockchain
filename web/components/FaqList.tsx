export interface FaqEntry {
  question: string;
  answer: string;
}

export default function FaqList({ items }: { items: FaqEntry[] }) {
  return (
    <dl className="flex flex-col gap-6">
      {items.map((item) => (
        <div key={item.question} className="border-t border-black/[.08] pt-6 dark:border-white/[.145]">
          <dt className="text-base font-semibold">{item.question}</dt>
          <dd className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">{item.answer}</dd>
        </div>
      ))}
    </dl>
  );
}
