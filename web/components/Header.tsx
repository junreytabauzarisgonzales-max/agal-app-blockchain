import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";

const links = [
  { href: "/", label: "Home" },
  { href: "/overview", label: "Overview" },
  { href: "/documentation", label: "Our Story" },
  { href: "/how-it-works", label: "How it works" },
  { href: "/manual", label: "Manual" },
  { href: "/tutorial", label: "Tutorial" },
  { href: "/news", label: "News" },
];

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-black/[.08] bg-background/85 backdrop-blur-sm dark:border-white/[.145]">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-4 py-4 sm:px-6">
        <Link href="/" className="text-lg font-semibold tracking-tight">
          Agal
        </Link>

        <nav aria-label="Main navigation" className="hidden gap-4 text-sm font-medium text-zinc-600 dark:text-zinc-400 lg:flex">
          {links.map((link) => (
            <Link key={link.href} href={link.href} className="transition-colors hover:text-foreground">
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2 sm:gap-3">
          <ThemeToggle />
          {/* No-JS mobile menu: a native disclosure widget, so navigation
              still works even if client script never hydrates. */}
          <details className="relative lg:hidden">
            <summary className="cursor-pointer list-none rounded-full border border-black/[.08] px-3 py-2 text-sm font-medium dark:border-white/[.145]">
              Menu
            </summary>
            <nav aria-label="Mobile navigation" className="absolute right-0 mt-2 flex w-48 flex-col gap-1 rounded-xl border border-black/[.08] bg-background p-2 shadow-lg dark:border-white/[.145]">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-zinc-600 hover:bg-black/[.05] dark:text-zinc-400 dark:hover:bg-white/[.08]"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </details>

          <Link
            href="/#download"
            className="rounded-full bg-accent px-3 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90 sm:px-4"
          >
            Download
          </Link>
        </div>
      </div>
    </header>
  );
}
