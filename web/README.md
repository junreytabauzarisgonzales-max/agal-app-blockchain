# Agal marketing site

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

## Running

```bash
npm install
npm run dev     # http://localhost:3000
npm run build   # static export to out/
```
