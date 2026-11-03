export interface NewsPost {
  slug: string;
  date: string; // ISO date
  title: string;
  summary: string;
  body: string[]; // paragraphs
}

/**
 * Static list of project updates -- no CMS/backend, since this site has no
 * login and is exported as static HTML. Add new entries at the top.
 */
export const newsPosts: NewsPost[] = [
  {
    slug: "tamper-evident-chain-of-custody",
    date: "2026-09-18",
    title: "A tamper-evident record for every batch",
    summary:
      "Every step a batch of seaweed takes -- harvested, dried, handed to a supplier, sold to a buyer -- is hashed and anchored on a public blockchain ledger. Anyone can verify a batch's full history hasn't been altered.",
    body: [
      "Every step a batch of seaweed takes -- harvested, dried, handed to a supplier, sold to a buyer, exported -- is recorded as its own permanent entry, never an edit to a previous one. That history is exactly what gets hashed and anchored on a public blockchain ledger, one fingerprint per event.",
      "No plaintext ever goes on-chain -- not a farmer's name, not a price, not a location. Just a cryptographic fingerprint, plus enough metadata to tell which batch it belongs to. Anyone who fetches a batch's recorded events from Agal can recompute the same fingerprint and confirm it still matches what's on-chain, which is what makes the history verifiable rather than just claimed.",
      "See How it works for the full step-by-step pipeline.",
    ],
  },
  {
    slug: "offline-first-farmer-app",
    date: "2026-09-18",
    title: "Designing for farmers with no signal",
    summary:
      "Tawi-Tawi's farmers can't count on always having a connection. The Farmer experience in the Agal app works fully offline -- harvests and handoffs are logged on the phone and sync automatically once a connection is available, with nothing ever lost or overwritten.",
    body: [
      "Tawi-Tawi's farmers can't count on always having a connection, so the Farmer experience in the Agal app had to work fully offline from the start -- not as a fallback mode, but as the default.",
      "Harvests and handoffs are logged straight to the phone the moment they happen. Once a connection is available, everything syncs to Agal's server automatically in the background. Because every logged action is its own permanent entry rather than an edit to something that might already exist elsewhere, there's no risk of two people's offline edits conflicting or overwriting each other when they both come back online.",
      "Supplier/Aggregator and Buyer/Exporter accounts assume a normal connection, since those roles are typically operating from somewhere with reception.",
    ],
  },
  {
    slug: "agal-project-kickoff",
    date: "2026-09-18",
    title: "Agal is underway",
    summary:
      "We've started building Agal for the Philippine Startup Challenge: a price-transparency and traceability platform for seaweed farmers, aggregators, and exporters in Tawi-Tawi. The backend, mobile app, and blockchain-backed chain-of-custody ledger are all in active development.",
    body: [
      "We've started building Agal for the Philippine Startup Challenge: a price-transparency and traceability platform for seaweed farmers, aggregators, and exporters in Tawi-Tawi.",
      "The plan spans four pieces working together: a role-based mobile app (Farmer, Supplier/Aggregator, Buyer/Exporter), a backend API that's the single source of truth for prices and chain-of-custody, a smart contract that anchors a tamper-evident hash of every event, and this site.",
      "Follow this page for updates as each piece comes online.",
    ],
  },
];
