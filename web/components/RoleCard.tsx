export default function RoleCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-black/[.08] p-6 dark:border-white/[.145]">
      <div className="h-1 w-8 rounded-full bg-accent" />
      <h3 className="mt-4 text-base font-semibold">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-zinc-600 dark:text-zinc-400">{description}</p>
    </div>
  );
}
