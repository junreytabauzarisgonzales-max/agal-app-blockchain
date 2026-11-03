import type { Metadata } from "next";
import Link from "next/link";
import ManualSection, { type ManualSectionData } from "@/components/ManualSection";

export const metadata: Metadata = { title: "User Manual" };

const sections: ManualSectionData[] = [
  {
    slug: "farmer",
    role: "Farmer",
    requiresConnectivity: "Harvests and outgoing messages work offline after sign-in.",
    steps: [
      "Create an account and choose \"Farmer\" as your role, or log in if you already have one.",
      "Tap Log New Harvest to enter the species, estimated weight, and harvest date. Tap Use Current Location to attach GPS coordinates, then Save Harvest Batch. The harvest is saved on your phone even with no signal.",
      "Open a batch to record Start Drying, then Finish Drying · Ready for Pickup. The receiving supplier confirms the custody transfer from their account.",
      "Keep an eye on the \"pending sync\" count at the top of your batch list -- it shows how many records are still waiting to reach the server. They sync automatically the next time you have a connection.",
      "Tap the message icon to chat directly with a Supplier or Buyer. Messages you write offline queue up and send once you're back online -- or tap the SMS icon in a chat to send that message as a regular text instead.",
      "Tap Today’s Buying Prices on Home while connected to compare posted offers. Open Profile for personal information, sync management, and the settings gear.",
    ],
    note: "You never need to be online to log a harvest or an update. Nothing is lost if you close the app or lose signal -- it's stored on your phone until it syncs.",
  },
  {
    slug: "supplier",
    role: "Supplier / Aggregator",
    requiresConnectivity: "Requires an internet connection.",
    steps: [
      "Create an account and choose \"Supplier / Aggregator\" as your role, or log in if you already have one.",
      "Home summarizes recorded sales and your inventory. Open Pickup Dashboard to find dried batches ready for pickup.",
      "Choose Verify & receive, check the batch history, and enter the scale weight and quality details. After receiving the harvest, tap Confirm Receipt & Record Transfer.",
      "Tap Bundle Batches into Shipment, enter a destination, choose your inventory batches, and tap Create Shipment. Check the recorded manifest and batch history for the shared shipment reference.",
      "Tap the message icon to chat directly with a Farmer or Buyer, or tap the SMS icon in a chat to reach them as a regular text instead.",
      "Open Profile for personal information and the settings gear for appearance, privacy, and other app options.",
    ],
    note: "A shipment manifest groups inventory batches. It does not by itself confirm delivery or transfer custody to a buyer.",
  },
  {
    slug: "buyer",
    role: "Buyer / Exporter",
    requiresConnectivity: "Requires an internet connection.",
    steps: [
      "Create an account and choose \"Buyer / Exporter\" as your role, or log in if you already have one.",
      "Your home screen lists batches currently with a supplier.",
      "Tap a batch to inspect its origin and handling history. Use Verify on Sepolia on an anchored event to compare its recorded data with the public ledger.",
      "Choose View & purchase to open the verification form. After receiving the purchase, complete the measurements and confirm the purchase transfer.",
      "Tap the message icon to chat directly with a Farmer or Supplier, or tap the SMS icon in a chat to reach them as a regular text instead.",
      "Open Profile for personal information and the settings gear for appearance, privacy, and other app options.",
    ],
    note: "Live verification needs a connection. A matching hash confirms the recorded event data matches the ledger; it does not independently inspect the physical harvest.",
  },
];

export default function ManualPage() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-10 px-6 py-16">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">User manual</h1>
        <p className="mt-3 text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          How to use Agal, whichever role you sign in as. All three are covered below --
          jump straight to yours.
        </p>
        <Link href="/tutorial" className="mt-5 inline-flex items-center gap-2 rounded-full bg-accent px-5 py-3 text-sm font-semibold text-accent-foreground transition-opacity hover:opacity-90">
          Follow the tutorial with screenshots <span aria-hidden="true">→</span>
        </Link>
        <nav className="mt-6 flex flex-wrap gap-2">
          {sections.map((section) => (
            <a
              key={section.slug}
              href={`#${section.slug}`}
              className="rounded-full border border-black/[.08] px-4 py-2 text-sm font-medium transition-colors hover:border-accent hover:text-accent dark:border-white/[.145]"
            >
              {section.role}
            </a>
          ))}
        </nav>
      </header>

      <div className="flex flex-col gap-10">
        {sections.map((section) => (
          <ManualSection key={section.slug} section={section} />
        ))}
      </div>
    </main>
  );
}
