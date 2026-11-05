import Link from "next/link";

const columns = [
  {
    title: "Product",
    links: [
      { href: "/overview", label: "Overview" },
      { href: "/documentation", label: "Documentation & Our Story" },
      { href: "/how-it-works", label: "How it works" },
      { href: "/manual", label: "User manual" },
      { href: "/tutorial", label: "App tutorial" },
      { href: "/faq", label: "FAQ" },
      { href: "/news", label: "News & updates" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/terms", label: "Terms of use" },
      { href: "/privacy", label: "Privacy policy" },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-black/[.08] bg-surface dark:border-white/[.145]">
      <div className="mx-auto grid max-w-5xl gap-10 px-6 py-12 sm:grid-cols-[1.5fr_1fr_1fr]">
        <div>
          <p className="text-lg font-semibold tracking-tight">Agal</p>
          <p className="mt-2 max-w-xs text-sm leading-6 text-zinc-600 dark:text-zinc-400">
            Price transparency and traceability for the seaweed supply chain in
            Tawi-Tawi. Built for the Philippine Startup Challenge.
          </p>
        </div>
        {columns.map((column) => (
          <div key={column.title}>
            <p className="text-sm font-semibold text-foreground">{column.title}</p>
            <ul className="mt-3 flex flex-col gap-2">
              {column.links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-zinc-600 transition-colors hover:text-foreground dark:text-zinc-400"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-black/[.08] px-6 py-6 dark:border-white/[.145]">
        <p className="mx-auto max-w-5xl text-xs text-zinc-500">
          &copy; {new Date().getFullYear()} Agal. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
