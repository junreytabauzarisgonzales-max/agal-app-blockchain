import { APPLE_STORE_URL, MICROSOFT_STORE_URL, PLAY_STORE_URL } from "@/lib/config";
import Image from "next/image";
import { DownloadIcon } from "@/components/Icons";
import release from "@/lib/android-release.json";

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
      className="rounded-2xl border border-black/[.08] bg-surface p-6 sm:p-8 dark:border-white/[.145]"
    >
      <div className="flex items-center gap-4">
        <Image src="/branding/agal-app-icon.png" alt="AGAL app icon" width={64} height={64} className="size-16 rounded-2xl" />
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">Android application</p>
          <h2 className="mt-1 text-xl font-semibold">Get the Agal app</h2>
        </div>
      </div>
      <p className="mt-2 max-w-md text-sm leading-6 text-zinc-600 dark:text-zinc-400">
        One app, three roles &mdash; Farmer, Supplier/Aggregator, and Buyer/Exporter.
        Sign in and Agal shows you the experience built for your role.
      </p>
      <div className="mt-6 rounded-xl border border-accent/20 bg-background p-5 sm:p-6">
        <div className="flex flex-col items-start justify-between gap-5 sm:flex-row sm:items-center">
          <div>
            <h3 className="font-semibold">Download for Android</h3>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">Version {release.version} · Build {release.build} · {(release.bytes / (1024 * 1024)).toFixed(1)} MiB</p>
            <p className="mt-1 text-xs leading-6 text-zinc-500 dark:text-zinc-400">Android 7.0 or later · Direct APK installation</p>
          </div>
          <a href={release.url} download={release.filename} className="inline-flex min-h-12 w-full shrink-0 items-center justify-center gap-3 rounded-full bg-accent px-6 py-3 text-sm font-semibold text-accent-foreground transition-opacity hover:opacity-90 sm:w-auto">
            <DownloadIcon /> Download APK
          </a>
        </div>
        <dl className="mt-5 grid gap-3 border-t border-black/[.08] pt-4 text-xs leading-6 sm:grid-cols-2 dark:border-white/[.145]">
          <div><dt className="text-zinc-500 dark:text-zinc-400">Release date</dt><dd>{release.releaseDate ?? "Not specified"}</dd></div>
          <div><dt className="text-zinc-500 dark:text-zinc-400">Release classification</dt><dd className="capitalize">{release.channel ?? "Not specified"}</dd></div>
        </dl>
        <details className="mt-5 border-t border-black/[.08] pt-4 dark:border-white/[.145]">
          <summary className="cursor-pointer text-sm font-medium text-accent">How to install</summary>
          <ol className="mt-4 list-decimal space-y-3 pl-5 text-sm leading-7 text-zinc-600 dark:text-zinc-400">
            <li>Download the APK on your Android device, then open it from your browser&apos;s downloads or Files app.</li>
            <li>If Android asks, allow installation from that browser or file manager in Settings. The option is usually called <strong>Install unknown apps</strong>; names vary by device.</li>
            <li>Return to the APK and tap <strong>Install</strong>. For an existing installation, Android may offer an update if its signing key matches.</li>
            <li>Open Agal and connect to the internet to sign in or activate your account. You can turn off the installation permission afterward.</li>
          </ol>
        </details>
        <details className="mt-4 border-t border-black/[.08] pt-4 dark:border-white/[.145]">
          <summary className="cursor-pointer text-sm font-medium text-accent">File details &amp; SHA-256</summary>
          <p className="mt-3 break-all text-xs leading-6 text-zinc-600 dark:text-zinc-400">{release.filename} · {release.bytes.toLocaleString("en-US")} bytes</p>
          <code className="mt-2 block break-all text-xs leading-6">{release.sha256}</code>
          <a href={`${release.url}.sha256`} download className="mt-3 inline-block min-h-10 py-2 text-xs font-medium text-accent underline underline-offset-4">Download checksum file</a>
        </details>
      </div>
      <h3 className="mt-8 text-sm font-semibold">App store availability</h3>
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
