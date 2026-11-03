export interface TutorialStep {
  id: string;
  title: string;
  screenshot: string;
  alt: string;
  caption: string;
  instructions: string[];
  tip?: string;
}

export interface TutorialGuide {
  id: string;
  number: string;
  role: string;
  title: string;
  summary: string;
  connectivity: string;
  account: string;
  steps: TutorialStep[];
}

export const tutorialGuides: TutorialGuide[] = [
  {
    id: "farmer",
    number: "01",
    role: "Farmer",
    title: "Log your harvest. Stay connected.",
    summary: "Start with a harvest on your phone, check buying offers, and reach your trading partners even when data is unavailable.",
    connectivity: "Harvests and outgoing messages work offline after sign-in",
    account: "Junrey Gonzales",
    steps: [
      {
        id: "farmer-home",
        title: "Get to know your home screen",
        screenshot: "farmer_dashboard",
        alt: "Junrey Gonzales’s farmer dashboard with an offline banner, pending sync count, buying prices shortcut, and a 180 kg Cottonii batch.",
        caption: "Home brings your saved batches, buying-price shortcut, and sync status together.",
        instructions: [
          "Open Home after signing in as a farmer. The status banner tells you whether your records are synced, pending, or offline.",
          "Review your batch counts and saved harvest cards. Tap Update status on a batch, or find it in the Batches tab.",
          "When you begin drying, tap Start Drying. When finished, tap Finish Drying · Ready for Pickup so a supplier can find the batch.",
        ],
        tip: "Tap the sync banner, or open Profile → Sync management, to see pending records and use Sync Now when connected.",
      },
      {
        id: "log-harvest",
        title: "Save a harvest without a connection",
        screenshot: "farmer_log_harvest_offline",
        alt: "Log New Harvest form showing species choices, a weight of 180 kg, harvest date and time, GPS controls, and Save Harvest Batch.",
        caption: "Your harvest is saved on your device first, including when you are offline.",
        instructions: [
          "From Home, tap Log New Harvest. Select Cottonii (Sakol) or Tambalang and enter the estimated weight in kilograms.",
          "Check the harvest date and time. Tap the date row to change them if you are logging an earlier harvest.",
          "Tap Use Current Location and allow location access to attach GPS coordinates. You can also save a harvest without a location.",
          "Tap Save Harvest Batch. Your record is stored locally and queued for sync when a connection is available.",
        ],
        tip: "GPS can work without mobile data. The map preview may still need a connection. Keep Agal open when reconnecting so pending records can sync.",
      },
      {
        id: "buying-prices",
        title: "Check today’s buying prices",
        screenshot: "farmer_buying_prices",
        alt: "Today’s Buying Prices screen with Cottonii and Tambalang filters and sample offers of PHP 55 and PHP 58 per kilogram.",
        caption: "Compare posted offers by species, grade, location, and effective date.",
        instructions: [
          "Connect to the internet, then tap Today’s Buying Prices on Home.",
          "Choose All species, Cottonii, or Tambalang to narrow the list.",
          "Read the price per kilogram, grade, location, effective date, and any buying conditions before contacting the trading partner.",
          "Pull down on the list to refresh the posted offers.",
        ],
        tip: "The figures in these screenshots are examples. Live offers come from suppliers and buyers; confirm the final price and grade with your trading partner.",
      },
      {
        id: "messages-sms",
        title: "Send a message or use SMS",
        screenshot: "farmer_sms_chat",
        alt: "A conversation between Junrey Gonzales and Hamsya Igasan about harvest pickup, with a draft location message and an orange Send via SMS button.",
        caption: "Use in-app messages when connected, or open your phone’s SMS composer.",
        instructions: [
          "Open Messages and choose a conversation. To start one, tap the compose icon and select a contact.",
          "Type your message and tap the send arrow. A farmer’s outgoing messages are saved and queued when offline.",
          "If the contact has a saved phone number, tap Send via SMS to open your phone’s messaging app with the number and draft filled in.",
          "Review the message and send it from your phone’s SMS app. Return to Agal to continue the in-app conversation.",
        ],
        tip: "SMS uses your mobile network and plan. Sending an SMS does not automatically add that text to the Agal chat history.",
      },
    ],
  },
  {
    id: "supplier",
    number: "02",
    role: "Supplier / Trader",
    title: "Manage your inventory and shipments.",
    summary: "Review recorded sales, receive ready harvests, and link inventory batches to a shared shipment manifest.",
    connectivity: "Internet required for inventory, receipt, and shipment recording",
    account: "Hamsya Igasan",
    steps: [
      {
        id: "supplier-dashboard",
        title: "Review sales and receive batches",
        screenshot: "supplier_dashboard",
        alt: "Hamsya Igasan’s supplier dashboard showing PHP 68,250 in sample recorded sales, three inventory batches, 550 kg, and a shipment button.",
        caption: "The dashboard summarizes payment records and batches currently in your inventory.",
        instructions: [
          "Sign in as a supplier and open Home. Review Recorded sales, Inventory batches, and the weight ready to bundle.",
          "Tap Pickup Dashboard to find dried batches ready for pickup. Search by farmer, batch, or location.",
          "Choose Verify & receive on an available batch. Check its provenance, enter the verified scale weight, moisture level, quality rating, and any remarks.",
          "After receiving the harvest, tap Confirm Receipt & Record Transfer. The batch becomes part of your supplier inventory.",
        ],
        tip: "Recorded sales summarize PHP payment events. They are not a wallet balance. Open an inventory batch to see its handling history.",
      },
      {
        id: "bundle-shipment",
        title: "Bundle inventory into a shipment",
        screenshot: "supplier_bundle_shipment",
        alt: "Bundle a Shipment form with an exporter destination and two selected batches totaling 400 kg.",
        caption: "Choose the batches you hold and give their shipment a destination.",
        instructions: [
          "From Home, tap Bundle Batches into Shipment.",
          "Enter the exporter or warehouse in Destination.",
          "Tick the inventory batches to include. Check the selected batch count and combined weight at the bottom of the form.",
          "Tap Create Shipment to record a shared shipment reference in each selected batch’s history.",
        ],
        tip: "Only batches currently held in your supplier inventory can be bundled. A manifest groups the batches; it does not itself confirm delivery or transfer custody to a buyer.",
      },
      {
        id: "shipment-recorded",
        title: "Check the recorded manifest",
        screenshot: "supplier_shipment_recorded",
        alt: "A recorded shipment manifest addressed to Krishane Ann Remonde’s Zamboanga warehouse, containing two batches and 400 kg.",
        caption: "The manifest lists its destination, membership, weight, and shipment reference.",
        instructions: [
          "Scroll to Shipment manifests below the bundling form to review the shipment you created.",
          "Look for Recorded, then check the destination, number of batches, total weight, and reference.",
          "Open a member batch’s provenance to see the shipment note added to its handling history.",
          "If recording was interrupted and the manifest remains a Draft, reconnect and use the retry control to finish recording the batch links.",
        ],
        tip: "Keep Agal open until recording completes. The saved manifest on this device helps you retry an interrupted request.",
      },
    ],
  },
  {
    id: "buyer",
    number: "03",
    role: "Buyer / Exporter",
    title: "Know where your seaweed came from.",
    summary: "Find available batches, inspect their origin, and follow the handling history before recording a purchase.",
    connectivity: "Internet required for marketplace and blockchain verification",
    account: "Krishane Ann Remonde",
    steps: [
      {
        id: "find-batch",
        title: "Find an available batch",
        screenshot: "exporter_marketplace",
        alt: "The Sourcing Marketplace with a search field, species and Nearby filters, and batches supplied by Hamsya Igasan.",
        caption: "Browse batches held by suppliers, or filter them by species and location.",
        instructions: [
          "Sign in as a buyer to open the Sourcing Marketplace on Home.",
          "Search by species, location, or supplier. Use the Cottonii and Tambalang filters, or Nearby after allowing location access.",
          "Tap a batch card to inspect its provenance. If you already have a full batch ID, open Batches and paste it into Look up any batch.",
          "When ready to record a received purchase, choose View & purchase, complete the verification form, and confirm the purchase transfer.",
        ],
        tip: "Use My purchases in the marketplace filters to find batches currently held by your buyer account.",
      },
      {
        id: "verify-origin",
        title: "Check the origin and verify a record",
        screenshot: "batch_verification_origin",
        alt: "Batch Provenance viewed by Krishane Ann Remonde, showing Junrey Gonzales as the originating farmer and a verified harvest record.",
        caption: "Start with the farmer and harvest record, then check the recorded drying and grading steps.",
        instructions: [
          "On Batch Provenance, check the batch ID, species, estimated weight, and originating farmer.",
          "Read the harvest entry for its date, actor, and available origin notes. Continue through drying and quality grading.",
          "For an anchored entry, tap Verify on Sepolia. The app compares that event’s data with the record on the public ledger.",
          "Read the result. A matching record means the event’s recorded data matches what was anchored on-chain.",
        ],
        tip: "Pending entries become verifiable after anchoring completes. If Sepolia cannot be reached, try verification again when your connection is available.",
      },
      {
        id: "handling-history",
        title: "Follow the full handling history",
        screenshot: "batch_verification_full_history",
        alt: "The batch handling timeline showing quality grading, supplier handover, payment, and a shipment note for the exporter’s warehouse.",
        caption: "The timeline keeps handling events and the account responsible for each step together.",
        instructions: [
          "Scroll through the timeline to review quality measurements, handovers, payments, and shipment notes.",
          "Check who recorded each step and when it occurred. Shipment notes identify the shared shipment reference and destination.",
          "Tap the copy icon next to a transaction hash if you need to share that transaction reference.",
          "Use the refresh icon to load new handling events or updated anchoring status.",
        ],
        tip: "Verification is per event. A matching hash confirms the recorded data has not changed; it does not independently inspect the physical harvest.",
      },
    ],
  },
];

export const tutorialQuestions = [
  {
    question: "What should I do before going offline?",
    answer: "Sign in while you have an internet connection. After that, farmers can save harvests, drying updates, and outgoing messages on the device. Account activation, current buying prices, supplier operations, and live verification need a connection.",
  },
  {
    question: "What does the pending sync count mean?",
    answer: "These are locally saved harvest events and messages that the server has not acknowledged yet. Tap the banner or open Profile → Sync management, reconnect, and tap Sync Now. Keep the app open while it syncs.",
  },
  {
    question: "Can I register without an internet connection?",
    answer: "Register Offline saves a secure registration draft on your device. Return to Sign up when connected to complete registration and activate the account before using the app.",
  },
  {
    question: "Where do I edit my profile or change settings?",
    answer: "Open the Profile tab. Personal information lets you edit your name, phone number, and municipality. The settings gear opens appearance, biometric login, privacy, and other app options. A saved phone number lets trading partners use the SMS fallback.",
  },
  {
    question: "What if sync or verification fails?",
    answer: "For harvests and farmer messages, keep the local records, reconnect, and retry from Sync management. For verification, refresh the batch history and retry Verify on Sepolia. A pending or failed anchor is not the same as a verified record.",
  },
];
