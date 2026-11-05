# Agal — Current Website Documentation

**Review date:** November 5, 2026

**Website source:** [`web/`](./)

**Review method:** Source review of website routes, shared components, content files, public assets, and deployment configuration, updated after the Home/theme enhancements. The static export was also checked in headless Chrome. No deployed website URL was supplied; production environment values, live store availability, and mobile workflows were not independently verified.

## 1. Executive summary

Agal's current website is a public information, onboarding, and app-discovery site for a seaweed price-transparency and harvest-traceability platform serving Tawi-Tawi, Philippines. It presents the project as an entry for the Philippine Startup Challenge.

The central message is:

> Fair prices. Verified harvests. Straight from Tawi-Tawi.

The website explains the product, introduces its three user roles, describes offline recording and blockchain-backed traceability, provides written and screenshot-based instructions, publishes project updates, offers an Android APK download, links to backend/contract infrastructure, and introduces the development team. Configured app-store links remain available alongside the APK.

### Current inventory

| Item | Current implementation |
| --- | --- |
| Content pages | 12: nine main pages and three individual news articles |
| Primary audience | Farmers, suppliers/aggregators/traders, and buyers/exporters |
| Written manual | Three role sections, with six steps each |
| Visual tutorial | Three role guides containing 10 screenshot walkthroughs |
| General FAQs | Nine; the first four also appear on the home page |
| Tutorial help | Five additional expandable questions |
| News | Three articles, all dated September 18, 2026 |
| App distribution | Direct Android APK, checksum, installation instructions, and three app-store slots |
| Themes | Persistent Light, Dark, and System selector; default System |
| Developers | One background-removed group photograph, mentor, and three student developers |
| Legal content | Privacy policy and terms of use, both marked as drafts |
| Language | English |
| Delivery | Static Next.js export |

## 2. Website purpose and product positioning

### Problems presented

- Farmers have limited visibility into fair seaweed market prices.
- Harvest origins and handling become difficult to trace as batches pass through the supply chain.
- Buyers and exporters need a way to inspect recorded provenance before purchasing.

### Benefits communicated

- Transparent buying-price information.
- Offline-first harvest recording for farmers.
- A shared, append-only chain-of-custody history.
- Cryptographic verification of recorded events through a public blockchain ledger.
- One app with role-specific experiences.
- Direct messaging and an SMS fallback.

These are descriptions of the Agal platform. The website itself provides information and navigation; it does not perform harvest logging, trading, messaging, or blockchain verification.

## 3. Page and route inventory

| Route | Page | Content and actions | Source |
| --- | --- | --- | --- |
| `/` | Home | Rotating Hero emblem, introduction, benefit badges, backend/contract cards, role cards, traceability preview, four FAQs, APK/store downloads, supporting links, and developers section | [`app/page.tsx`](app/page.tsx) |
| `/overview` | Project overview | Problem statement, three-role explanation, tamper-evident custody history, Tawi-Tawi context, and supporting links | [`app/overview/page.tsx`](app/overview/page.tsx) |
| `/how-it-works` | How it works | Five-stage record pipeline and an overview of the mobile, backend, and ledger layers | [`app/how-it-works/page.tsx`](app/how-it-works/page.tsx) |
| `/manual` | User manual | Farmer, Supplier/Aggregator, and Buyer/Exporter instructions, connectivity notes, role jump links, and a tutorial link | [`app/manual/page.tsx`](app/manual/page.tsx) |
| `/tutorial` | App tutorial | Getting-started guidance, role selection, 10 screenshots with instructions and tips, five help questions, and download/manual calls to action | [`app/tutorial/page.tsx`](app/tutorial/page.tsx) |
| `/faq` | Frequently asked questions | Nine static question-and-answer entries | [`app/faq/page.tsx`](app/faq/page.tsx) |
| `/news` | News & updates | Three entries with dates, summaries, and article links | [`app/news/page.tsx`](app/news/page.tsx) |
| `/news/tamper-evident-chain-of-custody` | A tamper-evident record for every batch | Explanation of permanent event history and public hash verification | [`lib/news.ts`](lib/news.ts) |
| `/news/offline-first-farmer-app` | Designing for farmers with no signal | Offline-first farmer recording and synchronization rationale | [`lib/news.ts`](lib/news.ts) |
| `/news/agal-project-kickoff` | Agal is underway | Project introduction and the mobile, backend, contract, and website components | [`lib/news.ts`](lib/news.ts) |
| `/terms` | Terms of use | Seven sections covering acceptance, intended users, information accuracy, blockchain permanence, acceptable use, availability, and contact | [`app/terms/page.tsx`](app/terms/page.tsx) |
| `/privacy` | Privacy policy | Account, harvest, message, and price data; blockchain publication; visibility; SMS; retention; and contact | [`app/privacy/page.tsx`](app/privacy/page.tsx) |

### Supporting routes and states

- `/sitemap.xml`: includes all 12 content-page URLs.
- `/robots.txt`: permits crawling and points to the sitemap.
- Custom 404 page: displays “Page not found” and a “Back to home” link.
- `/#download`: jumps to the app availability section on the home page.
- Individual news pages are generated from the static article list; unknown article slugs use the not-found behavior.

## 4. Home page content

The home page contains the following sections, in order:

1. **Hero:** the main tagline and a description of shared harvest records and current pricing.
2. **Benefit badges:** “Works offline,” “Blockchain-verified history,” and “One app, three roles.”
3. **Primary action:** “Learn to use the app,” linking to `/tutorial`.
4. **Infrastructure cards:** browser-checked backend health and the confirmed Sepolia contract, with full-address copying and an Etherscan link.
5. **Role cards:** Farmers; Suppliers & Aggregators; Buyers & Exporters.
6. **Pipeline preview:** record on the phone, synchronize, anchor event hashes, and verify history.
7. **FAQ preview:** the first four entries from the general FAQ collection.
8. **Download card:** direct Android APK, actual size/version, checksum, installation instructions, and the existing store slots.
9. **Further reading:** links to the project overview, user manual, and news.
10. **Developers:** mentor Ramat Hailaya and student developers Junrey Gonzales, Krishane Ann Remonde, and Moh. Hamsya Igasan, with the supplied group photograph immediately before the footer.

The decorative Hero emblem is derived from the existing app logo. It rotates every 75 seconds, has a native pause control, and becomes static for reduced-motion preferences. It does not receive pointer input.

The backend card checks `https://api-agal.msutcto.dev/health` once on mount and on manual retry, with an eight-second timeout. Only a successful response containing `{"status":"ok"}` is shown as Online. HTTP errors display Unavailable; blocked/network/timed-out or unrecognized responses display Unknown. This is API liveness, not database or blockchain readiness.

The contract card links to `0x3B7E22F9F7f323AB4E95AEDea84BDBf13465A3d3` on Sepolia Etherscan. It is explicitly identified as a smart contract, not a wallet.

The page has no live price feed, searchable batch list, or signed-in dashboard.

## 5. Role-based guidance

### Farmer

The manual and tutorial describe:

- Creating an account or signing in as a farmer.
- Reading dashboard batch counts, offline status, and pending sync information.
- Logging species, estimated weight, harvest date/time, and optional GPS coordinates.
- Selecting Cottonii (Sakol) or Tambalang in the demonstrated harvest workflow.
- Recording drying progress and marking a batch ready for pickup.
- Checking current buying prices by species, grade, location, effective date, and conditions while connected.
- Sending in-app messages, queuing outgoing messages offline, or opening the phone's SMS composer.
- Accessing profile information, settings, and sync management.

The detailed guidance says farmers must sign in while connected before using offline workflows. It also recommends keeping the app open during synchronization.

### Supplier / Aggregator / Trader

The manual and tutorial describe:

- Reviewing recorded sales and current inventory.
- Finding dried batches through the Pickup Dashboard.
- Inspecting provenance and entering scale weight, moisture, quality rating, and remarks.
- Confirming receipt and recording a custody transfer.
- Selecting inventory batches and recording a shipment destination and shared reference.
- Reviewing recorded manifests and retrying an interrupted draft.
- Messaging other roles and accessing profile/settings options.

Supplier operations require an internet connection. The guidance explicitly states that a shipment manifest groups batches but does not itself confirm delivery or transfer custody. Recorded sales are payment-event summaries, not a wallet balance.

### Buyer / Exporter

The manual and tutorial describe:

- Browsing the Sourcing Marketplace for supplier-held batches.
- Searching by species, location, or supplier and using species or Nearby filters.
- Looking up a batch using its full ID.
- Inspecting the originating farmer, harvest details, drying, grading, and custody history.
- Selecting “Verify on Sepolia” for an anchored event.
- Reviewing handovers, payments, shipment notes, and transaction references.
- Recording a received purchase through a verification/transfer form.
- Finding currently held batches through “My purchases.”

Buyer operations and live ledger verification require an internet connection. Verification is described as per-event: a matching hash confirms that recorded event data matches its anchor; it does not independently inspect the physical harvest.

## 6. Screenshot tutorial inventory

The tutorial uses demonstration accounts and sample records, prices, payment entries, and verification results. These examples are explicitly labeled on the page.

| Role | Walkthrough | Public image |
| --- | --- | --- |
| Farmer | Get to know your home screen | `tutorial/farmer_dashboard.webp` |
| Farmer | Save a harvest without a connection | `tutorial/farmer_log_harvest_offline.webp` |
| Farmer | Check today's buying prices | `tutorial/farmer_buying_prices.webp` |
| Farmer | Send a message or use SMS | `tutorial/farmer_sms_chat.webp` |
| Supplier / Trader | Review sales and receive batches | `tutorial/supplier_dashboard.webp` |
| Supplier / Trader | Bundle inventory into a shipment | `tutorial/supplier_bundle_shipment.webp` |
| Supplier / Trader | Check the recorded manifest | `tutorial/supplier_shipment_recorded.webp` |
| Buyer / Exporter | Find an available batch | `tutorial/exporter_marketplace.webp` |
| Buyer / Exporter | Check the origin and verify a record | `tutorial/batch_verification_origin.webp` |
| Buyer / Exporter | Follow the full handling history | `tutorial/batch_verification_full_history.webp` |

Each walkthrough has an image, descriptive alternative text, a caption, numbered instructions, and a contextual tip. Images open directly in a new tab at full size; there is no in-page image viewer. The asset documentation specifies 828 × 1792 pixels per image.

The tutorial also covers preparing for offline use, pending synchronization, offline registration drafts, profile/settings access, and failed sync or verification attempts. It explains that an offline registration draft must be completed online to activate an account.

**Content source:** [`lib/tutorial.ts`](lib/tutorial.ts)

**Images and asset notes:** [`public/tutorial/`](public/tutorial/)

## 7. FAQ and news content

### General FAQ topics

1. Offline use and the distinction between farmer and connected roles.
2. Tamper-evident batch history.
3. Data placed on the blockchain.
4. The three intended user roles.
5. Append-only events and concurrent actions.
6. Android, Windows, and planned iOS availability.
7. The absence of cryptocurrency payments or a token.
8. Backend-managed blockchain submissions.
9. Direct messaging and SMS fallback.

The general FAQ is displayed as an always-visible definition list. The five tutorial help questions use expandable native disclosure elements.

### News implementation

All three articles are dated **September 18, 2026**. Each has a slug, title, date, summary, and an array of body paragraphs. The listing follows the array order in [`lib/news.ts`](lib/news.ts); new entries are intended to be added at the top.

Article pages show the date, title, body paragraphs, and a “Back to news” link. There is no CMS, author profile, search, category filter, commenting, or pagination. Article bodies are plain paragraph strings; references such as “See How it works” are not automatically converted into links.

## 8. Navigation and visitor interactions

### Shared header

- Agal text wordmark linking to the home page.
- Desktop links: Home, Overview, How it works, Manual, Tutorial, and News.
- A persistent Download button linking to `/#download`.
- A Light/Dark/System selector that persists the visitor's preference.
- A smaller-screen Menu disclosure containing the same navigation links.
- Sticky positioning with a translucent background and backdrop blur.

### Shared footer

- Project description and Philippine Startup Challenge context.
- Product links: Overview, How it works, User manual, App tutorial, FAQ, and News & updates.
- Legal links: Terms of use and Privacy policy.
- Copyright year calculated when the static page is rendered at build time.

### Implemented browser interactions

- Internal page navigation and section-anchor links.
- Mobile menu expansion through native `<details>`/`<summary>`.
- Tutorial role/step jump links and “Back to role selection.”
- Full-size screenshots opening in a new tab.
- Expandable tutorial help answers.
- External store links when their URLs are configured.
- Direct APK and checksum downloads, with expandable installation/file details.
- Browser health checks, manual retry, and contract-address copying.
- Website-wide theme selection and optional Hero animation pausing.

No application forms, accounts, app chat, payment processing, harvest-entry tools, live marketplace, or batch verification interface are implemented in the website source. Those activities are described as app workflows.

## 9. App download availability

The home-page download card reads public build-time configuration from [`lib/config.ts`](lib/config.ts).

| Platform | Variable | Display when blank |
| --- | --- | --- |
| Android / Google Play | `NEXT_PUBLIC_PLAY_STORE_URL` | Coming soon |
| Windows / Microsoft Store | `NEXT_PUBLIC_MICROSOFT_STORE_URL` | Coming soon |
| iOS / Apple App Store | `NEXT_PUBLIC_APPLE_STORE_URL` | Planned |

A non-empty value creates an external link that opens in a new tab. The example environment file leaves all three values empty. The copy says Android and Windows launch first and iOS is a later target; the configuration comments say iOS is not yet in active development.

The local source alone does not establish which store links are enabled in production.

### Direct Android download

The existing home section also serves `/downloads/agal-1.0.0-build1.apk`. Its Android manifest was inspected: version **1.0.0**, build **1**, minimum SDK **24** (Android 7.0). The artifact is **67,789,535 bytes / 64.6 MiB**. A downloadable SHA-256 file and installation instructions are included.

The artifact was copied from the existing local release APK, not rebuilt. Release date and demo/beta/production classification are displayed as **Not specified** because they were not supplied. The metadata lives in [`lib/android-release.json`](lib/android-release.json); [`scripts/prepare-android-release.mjs`](scripts/prepare-android-release.mjs) prepares an approved replacement and its checksum. There is no separate `/download` route.

## 10. Visual design and accessibility provisions

### Design

- Text-focused layout with teal/seaweed-green accents, rounded cards, thin borders, pill buttons, and numbered steps.
- White and pale-gray surfaces in light mode; dark green-black surfaces in dark mode.
- Light/Dark/System selection with System as the default, local-storage persistence, and system-color-scheme updates. A synchronous root script resolves the theme before paint; CSS retains system-theme support without JavaScript.
- Geist Sans typography with Geist Mono also configured.
- Responsive layouts, including stacked cards on smaller screens and multi-column grids on larger screens.
- Content widths generally use `max-w-3xl` for articles and `max-w-5xl` for broader pages.
- Assets include app-icon-derived favicon/browser/touch icons, 10 tutorial screenshots, optimized Hero/app branding, the transparent team photograph, an APK/checksum, and five starter SVG files. The header retains its text wordmark.

### Accessibility provisions visible in source

- English document language and semantic headings, navigation, lists, figures, and definition lists.
- Native disclosure controls for the mobile menu and tutorial help.
- Descriptive screenshot alternative text and captions.
- Explicit new-tab descriptions on screenshot links.
- Visible focus styling on tutorial selection cards and screenshot links.
- Reduced-motion handling on tutorial hover transforms.
- Manual content for all three roles included directly in the static HTML.

Keyboard-focus provisions, responsive layouts, reduced motion, theme behavior, and no-JavaScript rendering were checked in headless Chrome. A full assistive-technology accessibility audit was not performed.

## 11. Privacy and terms content

Both legal pages are labeled **Draft — last updated September 2026**, with text stating they are working drafts for the Philippine Startup Challenge and have not been reviewed by legal counsel.

The privacy policy describes account information, harvest/custody records, messages, and posted prices. It states that plaintext personal/business data stays in Agal's database, that event hashes are published to the blockchain, that SMS is handed to the phone's messaging app, and that the marketing website has no login or personal-information collection. No analytics or advertising integration was found in the reviewed website source.

The terms describe intended users, responsibility for submitted information, permanent blockchain records, acceptable use, and the service's active-development status.

Both pages direct contact questions to channels announced on the news page. The current three news articles do not provide a concrete support email, phone number, or contact form.

## 12. Technical implementation and deployment

| Area | Current setup |
| --- | --- |
| Framework | Next.js 16.3.5, App Router |
| UI | React and React DOM 19.2.8 |
| Language | TypeScript |
| Styling | Tailwind CSS 4 and global CSS theme variables |
| Node requirement | 22.x |
| Rendering/output | `output: "export"`; static HTML/CSS/JavaScript in `out/` |
| Images | Next Image with image optimization disabled for export |
| Website data | Local TypeScript content arrays and inline page copy |
| Backend connection | Browser-only public `/health` check; no website API route handlers or application-data integration |
| Vercel | Next.js adapter, `.next` output metadata, clean URLs, no trailing slash |

The platform's Flutter app, REST API/PostgreSQL backend, and Ethereum test-network ledger are explained on the site. They are separate project components; their operational behavior is outside this website-content review.

### Metadata and discoverability

- Global title defaults to “Agal”; page-specific titles use the `%s · Agal` template.
- Global description explains traceability and transparent pricing.
- Open Graph and Twitter summary metadata are configured globally.
- How it works, Manual, Tutorial, FAQ, Terms, Privacy, and individual news articles define page titles.
- The tutorial also defines a page-specific description.
- Overview and the news listing currently inherit the global title.
- No dedicated social sharing image, explicit canonical-link configuration, or structured-data markup was found in the reviewed source.
- Sitemap static-page modification dates are generated at build time; article modification dates use the article dates.

### Site origin configuration

The origin used for metadata and sitemap URLs resolves in this order:

1. `NEXT_PUBLIC_SITE_URL`.
2. `VERCEL_PROJECT_PRODUCTION_URL`.
3. `VERCEL_URL`.
4. `http://localhost:3000`.

The configuration permits HTTP/HTTPS and normalizes the result to its origin. Public configuration changes require a rebuild.

### Existing commands

Run from `web/`:

```sh
npm ci
npm run dev
npm run lint
npm run build
```

`dev` starts local development; `lint` runs ESLint; `build` produces the static export. Vercel uses `.next` metadata through its Next.js adapter, while `out/` is intended for generic static hosting. See [`../DEPLOYMENT.md`](../DEPLOYMENT.md) for deployment details.

## 13. Current gaps and content inconsistencies

These observations identify the current content state and useful follow-up work; they do not establish a defect in the separate mobile app or backend.

| Observation | Source evidence | Suggested follow-up |
| --- | --- | --- |
| Support contact is indirect | Privacy and terms link to news, but current articles contain no contact channel | Publish an actual support/contact destination and link it from both pages |
| Legal pages remain drafts | Both explicitly carry the draft status and September 2026 date | Update their status and revision date when finalized |
| Store publication is configuration-dependent | The example values are blank, producing Coming soon/Planned states | Confirm deployed values when recording release availability |
| APK release details remain incomplete | The actual artifact version/size/checksum are known, but release date and classification were not supplied | Confirm these details before updating the release labels |
| Offline language varies in precision | Home, overview, FAQ, and older news use broad automatic-sync/no-loss language; the detailed tutorial adds prior sign-in, online activation, and keep-app-open guidance | Align high-level copy with the detailed operating conditions |
| Farmer handoff responsibility is described differently | General FAQ/older news describe farmers logging handoffs; the manual says the receiving supplier confirms transfer | Clarify the distinction between farmer status updates and supplier receipt confirmation |
| Marketplace terminology is ambiguous | One FAQ asks about a “real marketplace” and answers “No,” while the tutorial documents a Sourcing Marketplace | Reword the FAQ to distinguish seaweed sourcing from cryptocurrency trading/payment |
| Supplier role naming varies | Supplier/Aggregator, Suppliers & Aggregators, Supplier/Trader, and supplier are all used | Choose a consistent public role label or explain the equivalents |
| Blockchain payload wording varies | Several pages say “only” a fingerprint; the FAQ and news also mention batch IDs or metadata | Standardize the description of hashes and public identifiers |
| General concurrency language is absolute | The FAQ says there is “no conflict to resolve” because events append | Confirm the wording against actual custody/authorization rules before presenting it as an operational guarantee |
| Updates are concentrated on one date | All three news articles are dated September 18, 2026 | Add newer milestones as they become available |
| Some pages have generic metadata | Overview and the news listing inherit the global title and description | Add distinct page metadata for clearer search results |
| Website README is a setup-focused summary | It links to this complete inventory and documents the new enhancements | Keep this inventory and the release instructions aligned with later changes |

## 14. Content maintenance map

| Change needed | Primary file/location |
| --- | --- |
| Home sections and introductory copy | [`app/page.tsx`](app/page.tsx) |
| Project overview | [`app/overview/page.tsx`](app/overview/page.tsx) |
| Traceability pipeline explanation | [`app/how-it-works/page.tsx`](app/how-it-works/page.tsx) |
| Role-based written instructions | [`app/manual/page.tsx`](app/manual/page.tsx) |
| Tutorial role guides, steps, captions, alternative text, and help questions | [`lib/tutorial.ts`](lib/tutorial.ts) |
| Tutorial introduction and getting-started layout | [`app/tutorial/page.tsx`](app/tutorial/page.tsx) |
| Tutorial images | [`public/tutorial/`](public/tutorial/) |
| General FAQs and home FAQ preview content | [`lib/faq.ts`](lib/faq.ts) |
| News articles | [`lib/news.ts`](lib/news.ts) |
| Tagline, store links, and site origin logic | [`lib/config.ts`](lib/config.ts) |
| Store badge rendering and rollout copy | [`components/DownloadCard.tsx`](components/DownloadCard.tsx) |
| Android release metadata and packaging | [`lib/android-release.json`](lib/android-release.json), [`scripts/prepare-android-release.mjs`](scripts/prepare-android-release.mjs) |
| Theme initialization, persistence, and selector | [`lib/theme.ts`](lib/theme.ts), [`components/ThemeToggle.tsx`](components/ThemeToggle.tsx) |
| Backend status and contract card | [`components/ApiHealthCard.tsx`](components/ApiHealthCard.tsx), [`lib/health.ts`](lib/health.ts), [`components/ContractCard.tsx`](components/ContractCard.tsx) |
| Team layout and approved photo | [`components/DevelopersSection.tsx`](components/DevelopersSection.tsx), [`public/team/`](public/team/) |
| Shared navigation | [`components/Header.tsx`](components/Header.tsx), [`components/Footer.tsx`](components/Footer.tsx) |
| Global metadata and fonts | [`app/layout.tsx`](app/layout.tsx) |
| Colors and theme variables | [`app/globals.css`](app/globals.css) |
| Legal text | [`app/privacy/page.tsx`](app/privacy/page.tsx), [`app/terms/page.tsx`](app/terms/page.tsx) |
| Sitemap and crawler settings | [`app/sitemap.ts`](app/sitemap.ts), [`app/robots.ts`](app/robots.ts) |
| Build/export and hosting settings | [`next.config.ts`](next.config.ts), [`vercel.json`](vercel.json) |

## 15. Review boundaries

This inventory was cross-checked against website source, asset names, package versions, and hosting configuration. ESLint and the static production build passed. Headless Chrome checks covered all 12 content routes, theme persistence/system/blocked-storage behavior, simulated health-response success and failure, clipboard copying, responsive layouts, reduced motion, and no-JavaScript content. The served APK's byte count and SHA-256 matched its published metadata. It is not a claim that production matches these files or that the separate mobile workflows have passed end-to-end testing.
