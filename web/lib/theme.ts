export type ThemePreference = "light" | "dark" | "system";

export const THEME_STORAGE_KEY = "agal-theme";

export function parseTheme(value: string | null | undefined): ThemePreference {
  return value === "light" || value === "dark" ? value : "system";
}

// A fixed, trusted script runs before paint; no user input is interpolated.
// Keep resolution in sync with applyTheme below, including storage failure.
export const THEME_INIT_SCRIPT = `(function(){var p="system";try{var s=localStorage.getItem("${THEME_STORAGE_KEY}");if(s==="light"||s==="dark")p=s;}catch(e){}var d=p==="dark"||(p==="system"&&matchMedia("(prefers-color-scheme: dark)").matches);document.documentElement.dataset.theme=d?"dark":"light";document.documentElement.dataset.themePreference=p;})();`;

export function applyTheme(preference: ThemePreference) {
  const dark = preference === "dark" || (preference === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  document.documentElement.dataset.themePreference = preference;
}
