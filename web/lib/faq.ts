export interface FaqEntry {
  question: string;
  answer: string;
}

export const faqs: FaqEntry[] = [
  {
    question: "Does Agal work without an internet connection?",
    answer:
      "For farmers, yes. The Farmer experience is fully offline-first: harvests and handoffs are logged straight to the phone and sync automatically once a connection is available. Nothing is ever lost or overwritten. Supplier/Aggregator and Buyer/Exporter accounts assume a normal connection.",
  },
  {
    question: "How is a batch's history kept tamper-evident?",
    answer:
      "Every recorded step -- harvested, dried, transferred, sold, exported -- is hashed and anchored on a public blockchain ledger. No farm or business data is stored on-chain, only a cryptographic fingerprint, so anyone can independently verify the recorded history hasn't been altered. See How it works for the full pipeline.",
  },
  {
    question: "What actually gets stored on the blockchain?",
    answer:
      "Just a hash per event, plus the id of the batch it belongs to -- never plaintext data like names, weights, prices, or locations. The plaintext lives only in Agal's own database; the chain only ever sees an opaque fingerprint of it.",
  },
  {
    question: "Who is Agal built for?",
    answer:
      "Three roles in one app: Farmers, Suppliers/Aggregators, and Buyers/Exporters. Each role gets the screens and workflow suited to it, chosen automatically after sign-in. See the user manual for what each role can do.",
  },
  {
    question: "What happens if two people edit the same batch at once?",
    answer:
      "Nothing is ever edited in place -- every action (harvested, dried, transferred, and so on) is appended as its own new record rather than overwriting an old one. That means there's no conflict to resolve: two people acting on the same batch just produce two more entries in its history, in the order they happened.",
  },
  {
    question: "Which platforms will Agal be available on?",
    answer:
      "Android and Windows are launching first, via the Google Play Store and Microsoft Store. iOS support is planned for a later release.",
  },
  {
    question: "Is this connected to real cryptocurrency or a real marketplace?",
    answer:
      "No. The blockchain ledger is used purely as a tamper-evident record-keeping tool -- there's no token, no trading, and no cryptocurrency payment involved anywhere in Agal.",
  },
  {
    question: "Can Farmers or Suppliers interact with the blockchain directly?",
    answer:
      "No, and they don't need to. Only Agal's own backend service ever submits data to the ledger, using its own wallet. Farmers, Suppliers, and Buyers just use the app normally.",
  },
  {
    question: "Can I message another Agal user directly?",
    answer:
      "Yes -- every role can chat directly with any other Farmer, Supplier/Aggregator, or Buyer/Exporter from within the app. A Farmer composing a message offline has it queued and sent automatically once they're back online, just like a harvest record. Any chat also has a one-tap option to send that message as a regular SMS text instead, for when you'd rather reach someone over the phone network than the app.",
  },
];
