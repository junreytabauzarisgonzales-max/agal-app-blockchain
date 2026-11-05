import Image from "next/image";

const students = ["Junrey Gonzales", "Krishane Ann Remonde", "Moh. Hamsya Igasan"];

export default function DevelopersSection() {
  return (
    <section aria-labelledby="developers-heading" className="overflow-hidden border-t border-black/[.08] bg-surface dark:border-white/[.145]">
      <div className="mx-auto max-w-5xl px-6 py-16 sm:py-20">
        <header className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-accent">The people behind the platform</p>
          <h2 id="developers-heading" className="mt-4 text-2xl font-semibold leading-tight tracking-tight sm:text-3xl">MEET THE AGAL DEVELOPERS</h2>
          <p className="mt-4 text-base leading-7 text-zinc-600 dark:text-zinc-400">The team behind AGAL — working toward a more transparent and traceable seaweed industry.</p>
        </header>
        <div className="relative isolate mx-auto mt-10 max-w-4xl px-2 pt-6 sm:px-8 sm:pt-10">
          <div aria-hidden="true" className="pointer-events-none absolute inset-x-3 bottom-0 -z-10 h-3/4 rounded-t-[50%] bg-gradient-to-t from-accent/15 to-accent/[.025] sm:inset-x-8" />
          <Image
            src="/team/agal-developers.webp"
            alt="The AGAL team together: mentor Ramat Hailaya and student developers Junrey Gonzales, Krishane Ann Remonde, and Moh. Hamsya Igasan."
            width={1600}
            height={1162}
            sizes="(max-width: 768px) 90vw, 832px"
            className="h-auto w-full"
          />
        </div>
        <div className="mx-auto max-w-4xl border-t border-accent/20 pt-8 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">Mentor</p>
          <p className="mt-2 text-xl font-semibold">Ramat Hailaya</p>
          <p className="mt-8 text-xs font-semibold uppercase tracking-[0.16em] text-accent">Student Developers</p>
          <ul className="mt-4 grid gap-4 sm:grid-cols-3">
            {students.map(name => <li key={name} className="text-base font-medium sm:text-lg">{name}</li>)}
          </ul>
        </div>
      </div>
    </section>
  );
}
