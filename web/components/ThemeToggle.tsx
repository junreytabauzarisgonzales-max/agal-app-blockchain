"use client";

import { useSyncExternalStore } from "react";
import { applyTheme, parseTheme, THEME_STORAGE_KEY } from "@/lib/theme";

const changeEvent = "agal-theme-change";

function getPreference() {
  return parseTheme(document.documentElement.dataset.themePreference);
}

function subscribe(onChange: () => void) {
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  const handleSystem = () => {
    applyTheme(getPreference());
    onChange();
  };
  const handleStorage = (event: StorageEvent) => {
    if (event.key === THEME_STORAGE_KEY || event.key === null) {
      applyTheme(parseTheme(event.newValue));
      onChange();
    }
  };

  // Re-resolve if the system changed between the initial script and hydration.
  applyTheme(getPreference());
  media.addEventListener("change", handleSystem);
  window.addEventListener("storage", handleStorage);
  window.addEventListener(changeEvent, onChange);
  return () => {
    media.removeEventListener("change", handleSystem);
    window.removeEventListener("storage", handleStorage);
    window.removeEventListener(changeEvent, onChange);
  };
}

export default function ThemeToggle() {
  const preference = useSyncExternalStore(subscribe, getPreference, () => "system");

  return (
    <label className="theme-control flex items-center">
      <span className="sr-only">Color theme</span>
      <select
        value={preference}
        onChange={(event) => {
          const next = parseTheme(event.target.value);
          applyTheme(next);
          try {
            window.localStorage.setItem(THEME_STORAGE_KEY, next);
          } catch {
            // The selection still works for this visit if storage is blocked.
          }
          window.dispatchEvent(new Event(changeEvent));
        }}
        className="min-h-10 w-[5.5rem] cursor-pointer rounded-full border border-black/[.12] bg-background px-2 text-xs font-medium text-foreground sm:w-24 sm:px-3 sm:text-sm dark:border-white/20"
      >
        <option value="system">System</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
    </label>
  );
}
