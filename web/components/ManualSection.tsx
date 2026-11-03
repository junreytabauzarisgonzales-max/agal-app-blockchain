export interface ManualSectionData {
  slug: string;
  role: string;
  requiresConnectivity: string;
  steps: string[];
  note?: string;
}

/**
 * Renders fully in static HTML -- no client-side state hiding the other
 * roles. A manual that only shows its content after JavaScript hydrates is
 * one broken chunk load away from looking like it only covers one role.
 */
export default function ManualSection({ section }: { section: ManualSectionData }) {
  return (
    <section id={section.slug} className="border-t border-black/[.08] pt-10 dark:border-white/[.145]">
      <div className="flex items-baseline justify-between gap-4">
        <h2 className="text-2xl font-semibold">{section.role}</h2>
        <span className="text-sm text-zinc-500">{section.requiresConnectivity}</span>
      </div>
      <ol className="mt-6 flex flex-col gap-4">
        {section.steps.map((step, index) => (
          <li key={step} className="flex gap-4">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent text-xs font-semibold text-accent-foreground">
              {index + 1}
            </span>
            <span className="leading-6 text-zinc-700 dark:text-zinc-300">{step}</span>
          </li>
        ))}
      </ol>
      {section.note && (
        <p className="mt-6 rounded-lg border border-dashed border-black/[.15] p-4 text-sm text-zinc-500 dark:border-white/[.2]">
          {section.note}
        </p>
      )}
    </section>
  );
}
