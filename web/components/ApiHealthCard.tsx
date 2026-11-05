"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { BACKEND_HEALTH_URL } from "@/lib/config";
import { checkBackendHealth, type HealthResult } from "@/lib/health";
import { ExternalLinkIcon } from "@/components/Icons";

const labels = { online: "Online", unavailable: "Unavailable", unknown: "Unknown" };

export default function ApiHealthCard() {
  const [result, setResult] = useState<HealthResult>({ status: "unknown", detail: "Checking the public health endpoint…" });
  const [checking, setChecking] = useState(true);
  const [checkedAt, setCheckedAt] = useState<string | null>(null);
  const pending = useRef<AbortController | null>(null);

  const check = useCallback(async () => {
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    const timeout = window.setTimeout(() => controller.abort(), 8000);
    const next = await checkBackendHealth(controller.signal);
    window.clearTimeout(timeout);
    if (pending.current === controller) {
      setResult(next);
      setChecking(false);
      setCheckedAt(new Date().toISOString());
    }
  }, []);

  useEffect(() => {
    void check();
    return () => {
      pending.current?.abort();
      pending.current = null;
    };
  }, [check]);

  return (
    <article className="flex flex-col rounded-2xl border border-black/[.08] bg-surface p-6 dark:border-white/[.145]">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="font-semibold">AGAL Backend API</h3>
        <span role="status" className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${!checking && result.status === "online" ? "bg-accent/10 text-accent" : "bg-black/5 text-zinc-600 dark:bg-white/10 dark:text-zinc-300"}`}>
          <span aria-hidden="true" className="size-1.5 rounded-full bg-current" />
          {checking ? "Checking…" : labels[result.status]}
        </span>
      </div>
      <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">The service behind Agal&apos;s app.</p>
      <p className="mt-2 break-all font-mono text-xs text-foreground">api-agal.msutcto.dev/health</p>
      <p className="mt-4 min-h-16 text-xs leading-6 text-zinc-600 dark:text-zinc-400">{result.detail}</p>
      <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-3 text-sm">
        <a href={BACKEND_HEALTH_URL} target="_blank" rel="noopener noreferrer" className="inline-flex min-h-10 items-center gap-2 font-medium text-accent underline underline-offset-4">
          Open health endpoint <ExternalLinkIcon /><span className="sr-only"> (opens in a new tab)</span>
        </a>
        <button type="button" disabled={checking} onClick={() => { setChecking(true); setResult({ status: "unknown", detail: "Checking the public health endpoint…" }); void check(); }} className="min-h-10 text-xs font-medium text-zinc-600 underline underline-offset-4 disabled:cursor-wait disabled:opacity-60 dark:text-zinc-400">
          Check again
        </button>
      </div>
      <p className="mt-3 text-xs text-zinc-500 dark:text-zinc-400">
        {checkedAt ? <>Last checked <time dateTime={checkedAt}>{new Date(checkedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time> · Not continuously monitored</> : "Checked from your browser; status may vary by connection."}
      </p>
    </article>
  );
}
