import Image from "next/image";
import type { TutorialStep as TutorialStepData } from "@/lib/tutorial";

export default function TutorialStep({ step, number }: { step: TutorialStepData; number: number }) {
  const image = `/tutorial/${step.screenshot}.webp`;

  return (
    <article id={step.id} className="scroll-mt-28 overflow-hidden rounded-2xl border border-black/[.08] bg-surface dark:border-white/[.145]">
      <div className="border-b border-black/[.08] px-5 py-6 sm:px-7 dark:border-white/[.145]">
        <div className="flex items-start gap-3">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-semibold text-accent-foreground">
            {number}
          </span>
          <h3 className="pt-0.5 text-lg font-semibold tracking-tight">{step.title}</h3>
        </div>
      </div>

      <figure className="px-5 pt-7 sm:px-7">
        <a
          href={image}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`Open full-size screenshot: ${step.title} (opens in a new tab)`}
          className="group mx-auto block max-w-64 rounded-[1.75rem] border-[5px] border-[#203c32] bg-[#001f1b] shadow-lg transition-transform hover:-translate-y-1 motion-reduce:transform-none focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent"
        >
          <Image
            src={image}
            alt={step.alt}
            width={828}
            height={1792}
            sizes="(max-width: 640px) 75vw, 256px"
            className="h-auto w-full rounded-[1.4rem]"
          />
        </a>
        <figcaption className="mx-auto mt-4 max-w-sm text-center text-xs leading-5 text-zinc-600 dark:text-zinc-400">
          {step.caption}
          <a href={image} target="_blank" rel="noopener noreferrer" className="mt-1 block font-medium text-accent underline decoration-accent/40 underline-offset-4">
            Open full-size screenshot <span aria-hidden="true">↗</span>
            <span className="sr-only"> (opens in a new tab)</span>
          </a>
        </figcaption>
      </figure>

      <div className="px-5 pb-6 pt-6 sm:px-7">
        <ol className="space-y-4">
          {step.instructions.map((instruction, index) => (
            <li key={instruction} className="flex gap-3 text-sm leading-6 text-zinc-700 dark:text-zinc-300">
              <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border border-accent/25 text-[10px] font-semibold text-accent">
                {index + 1}
              </span>
              <span>{instruction}</span>
            </li>
          ))}
        </ol>
        {step.tip && (
          <p className="mt-6 rounded-xl border border-accent/15 bg-accent/5 p-4 text-xs leading-6 text-zinc-600 dark:text-zinc-400">
            <span className="font-semibold text-accent">Good to know. </span>{step.tip}
          </p>
        )}
      </div>
    </article>
  );
}
