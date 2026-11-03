import { APPLE_STORE_URL, MICROSOFT_STORE_URL, PLAY_STORE_URL } from "@/lib/config";

function StoreBadge({
  href,
  label,
  status,
}: {
  href: string;
  label: string;
  status: "coming-soon" | "planned";
}) {
  if (!href) {
    return (
      <span className="flex h-14 w-full items-center justify-between gap-3 rounded-xl border border-dashed border-black/[.15] px-5 text-left dark:border-white/[.2] sm:w-64">
        <span className="text-sm font-medium text-zinc-500 dark:text-zinc-400">{label}</span>
        <span className="rounded-full bg-black/[.05] px-2.5 py-1 text-xs font-medium text-zinc-500 dark:bg-white/[.08] dark:text-zinc-400">
          {status === "planned" ? "Planned" : "Coming soon"}
        </span>
      </span>
    );
  }
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="flex h-14 w-full items-center justify-center rounded-xl bg-foreground px-5 text-sm font-medium text-background transition-opacity hover:opacity-90 sm:w-64"
    >
      {label}
    </a>
  );
}

export default function DownloadCard() {
  return (
    <div
      id="download"
      className="rounded-2xl border border-black/[.08] bg-surface p-8 dark:border-white/[.145]"
    >
      <h2 className="text-xl font-semibold">Get the Agal app</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-zinc-600 dark:text-zinc-400">
        One app, three roles &mdash; Farmer, Supplier/Aggregator, and Buyer/Exporter.
        Sign in and Agal shows you the experience built for your role.
      </p>
      <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
        <StoreBadge href={PLAY_STORE_URL} label="Google Play" status="coming-soon" />
        <StoreBadge href={MICROSOFT_STORE_URL} label="Microsoft Store" status="coming-soon" />
        <StoreBadge href={APPLE_STORE_URL} label="Apple App Store" status="planned" />
      </div>
      <p className="mt-4 text-xs text-zinc-500">
        Android and Windows are launching first. iOS support is planned for a later release.
      </p>
    </div>
  );
}
