# Agal marketing site

See [Current Website Documentation](CURRENT_WEBSITE_DOCUMENTATION.md) for the
full page inventory, content analysis, feature descriptions, and current gaps.

For the Vercel root-directory settings and public environment variables, see
[DEPLOYMENT.md](../DEPLOYMENT.md). The included `vercel.json` uses Vercel's
Next.js adapter with `.next` build metadata and clean URLs, including the
screenshot tutorial at `/tutorial`. Do not override Vercel's Output Directory
to `out`; the adapter handles the static export automatically.

Static Next.js site (App Router) for Agal: a home page, project overview,
a news/updates section, and download buttons for the Play Store and
Microsoft Store listings. No login, no server-side logic -- `next.config.ts`
sets `output: "export"`, so `npm run build` produces plain static
HTML/CSS/JS in `out/` that can be hosted anywhere (Vercel, Netlify, S3 +
CloudFront, GitHub Pages, etc.).

## Structure

- `app/page.tsx` -- home page.
- `app/overview/page.tsx` -- project overview.
- `app/news/page.tsx` -- news/updates, sourced from the static list in `lib/news.ts`. Add new entries at the top of that array; there's no CMS or backend involved.
- `app/tutorial/page.tsx` -- the role-by-role screenshot tutorial, with content in `lib/tutorial.ts` and images in `public/tutorial/`.
- `components/DownloadCard.tsx` -- renders store links configured with the `NEXT_PUBLIC_*_STORE_URL` environment variables. Unpublished listings remain "Coming soon" / "Planned" badges.
- `lib/config.ts` -- public site metadata and store links. Copy `.env.example` to `.env.local` for local overrides; Vercel can supply the production site URL automatically.

## Home enhancements

- The Hero uses an optimized derivative of the app's existing logo. Its 75-second
  rotation can be paused and stops for reduced-motion preferences.
- Backend health is checked from the visitor's browser, with an eight-second
  timeout and a manual retry. Only a successful `{"status":"ok"}` response is
  labeled Online; blocked or failed checks are Unknown. This is a liveness check,
  not a database or blockchain readiness probe.
- The Sepolia contract card links to the confirmed deployed contract and copies
  its full address. Public endpoints are maintained in `lib/config.ts`.
- Light, Dark, and System preferences are available in the header. System is the
  default; the explicit preference is saved as `agal-theme` in local storage.
  A synchronous theme script prevents a wrong-theme flash on full page loads.
- The existing `/#download` section includes the approved Android APK, actual
  size, installation guidance, and SHA-256. Store buttons retain their existing
  configuration. No dedicated download route is required.
- The developers section uses the supplied group photo with only its background
  removed. The source photo and original app branding remain unchanged.
- `app/favicon.ico`, `app/icon.png`, and `app/apple-icon.png` use the app's existing
  dark launcher artwork.

### Updating the Android download

The current artifact was copied from
`apps/agal/build/app/outputs/flutter-apk/app-release.apk`. Its Android manifest
reports version **1.0.0**, build **1**, minimum SDK **24** (Android 7.0). It was not
rebuilt as part of the website update. Release date and demo/beta/production
classification remain unspecified until confirmed by the team.

For an approved replacement, inspect its manifest with Android's `aapt dump
badging` first, then run from `web`:

```sh
npm run release:prepare -- --source "../apps/agal/build/app/outputs/flutter-apk/app-release.apk" --version 1.0.0 --build 1 --min-sdk 24
```

Use the actual replacement artifact's version/build/min-sdk values. Optional
`--release-date YYYY-MM-DD` and `--channel demo|beta|production` arguments must be
provided only when confirmed. The script copies the artifact into
`public/downloads/`, writes a checksum file, and regenerates
`lib/android-release.json`; the card reads that metadata. Keep these files
together when updating a release. The narrow `.gitignore` exception includes
approved public download APKs while other APKs remain ignored.

Visual assets are in `public/branding/` and `public/team/`. The photograph's
alternative text lists team membership rather than guessing left-to-right
identities. All existing routes, tutorial screenshots, metadata, static export,
and Vercel build settings remain in place.

## Running

```bash
npm install
npm run dev     # http://localhost:3000
npm run build   # static export to out/
```
