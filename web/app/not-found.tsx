import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center gap-4 px-6 py-24 text-center">
      <p className="text-sm font-medium text-accent">404</p>
      <h1 className="text-3xl font-semibold tracking-tight">Page not found</h1>
      <p className="max-w-md leading-7 text-zinc-600 dark:text-zinc-400">
        The page you&apos;re looking for doesn&apos;t exist, or may have moved.
      </p>
      <Link
        href="/"
        className="mt-4 rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-90"
      >
        Back to home
      </Link>
    </main>
  );
}
