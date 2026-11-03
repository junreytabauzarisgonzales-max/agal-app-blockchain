# Deploy Agal to Vercel

Create **two Vercel projects** from this project directory. The Flutter app and
Solidity project are not Vercel build roots.

| Project | Root Directory | Framework | Runtime | Build / output |
| --- | --- | --- | --- | --- |
| Backend API | `backend` | FastAPI | Python 3.12 | Auto-detected `app/main.py:app`; no custom output directory |
| Website | `web` | Next.js | Node.js 22.x | `npm ci`, `npm run build`, output `out` |

These paths are relative to the directory containing this file. If the Git
repository includes an enclosing `Agal-master` folder, use `Agal-master/backend`
and `Agal-master/web` instead. Deploy the projects independently.

## 1. Prepare secrets and the database

From `backend`, with its Python dependencies installed:

```sh
python scripts/generate_secrets.py
```

This fills a missing/placeholder `SECRET_KEY` and `CRON_SECRET` in the ignored
local `backend/.env`, without printing either value. It preserves existing
non-placeholder secrets. Use `--rotate` only when intentionally rotating both;
changing `SECRET_KEY` invalidates previously issued mobile JWTs.

Use an external PostgreSQL service such as Neon. The backend accepts both
`postgresql://...` and `postgresql+asyncpg://...` URLs and translates provider
`sslmode` parameters for asyncpg. Vercel instances use `NullPool` and disable
prepared-statement caches for transaction-pooler compatibility.

Apply the existing migrations **once before deploying** to the chosen database:

```sh
# Run from backend with DATABASE_URL pointing at the deployment database.
python -m alembic upgrade head
```

For this migration command, prefer the database provider's direct connection
URL. The API can use its pooled connection URL. Do not run migrations on every
API request or automatically during concurrent preview builds.

## 2. Configure the backend Vercel project

Add these environment variables in **Settings → Environment Variables**. Use
the existing values from local configuration where appropriate; never put
secret values into `vercel.json`.

| Variable | Value |
| --- | --- |
| `ENVIRONMENT` | `production` (also set by `backend/vercel.json`) |
| `DATABASE_URL` | External PostgreSQL URL, with the provider's SSL settings |
| `SECRET_KEY` | The generated value from `backend/.env`, at least 32 random characters |
| `CRON_SECRET` | The separate generated value from `backend/.env` |
| `CORS_ORIGINS` | Exact website origin, for example `https://your-web-project.vercel.app`; comma-separate a custom domain if needed |
| `WEB3_PROVIDER_URL` | Sepolia RPC URL |
| `HARVEST_LEDGER_ADDRESS` | Existing deployed HarvestLedger address |
| `SERVICE_WALLET_PRIVATE_KEY` | Existing funded wallet authorized by HarvestLedger |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Optional; defaults to `1440` |

Vercel supplies `VERCEL=1`. The backend then enforces production secret checks
and uses serverless-safe database connections. Keep Preview and Production
database/wallet configuration separate if preview deployments will write data.
The existing Solidity contract does not need redeployment for this setup.

### Optional admin UI

To enable `/admin` on Vercel, configure all five values below:

- `ADMIN_EMAIL`
- `ADMIN_PASSWORD` — at least 12 characters
- `ADMIN_SESSION_SECRET` — an independent random secret of at least 32 characters
- `UPSTASH_REDIS_REST_URL` — HTTPS REST URL of an Upstash Redis database
- `UPSTASH_REDIS_REST_TOKEN`

Redis stores sessions, one-shot notifications, and login throttling across
serverless instances. Logout revokes the shared session. Without Redis, the
admin UI can still run in a single local process; production Vercel deployments
with admin credentials configured require Redis. To deploy the mobile API
without the admin UI, leave the three `ADMIN_*` credentials unset.

### Blockchain jobs on Vercel

Normal writes still attempt anchoring after their API response. Committed
pending/failed events survive interrupted invocations and can be recovered by
the authenticated route:

```text
GET /internal/cron/chain-anchors
Authorization: Bearer <CRON_SECRET>
```

Vercel sends that header automatically when the backend project has
`CRON_SECRET` configured. The route is excluded from the public API schema,
processes at most one event per invocation, and never caches its response.

The included cron schedule is **daily at 00:00 UTC**, compatible with Vercel
Hobby. It is a recovery safety net, not a continuous worker. On a plan that
permits frequent cron runs, change its schedule in `backend/vercel.json` to
`* * * * *` and redeploy for minute-by-minute recovery. For a larger backlog,
run the existing worker on a persistent host using the same database:

```sh
python -m app.workers.chain_anchors --retry-failed
```

A long-running Python worker process is not launched inside a Vercel Function.
The API function has a 300-second duration budget; normal background work that
exceeds it remains recoverable from the committed event table.

## 3. Configure the website Vercel project

`web/vercel.json` configures the Next.js static export and clean URLs, including
`/tutorial`, `/manual`, and `/news/...`.

Optional public build-time environment variables:

| Variable | Purpose |
| --- | --- |
| `NEXT_PUBLIC_SITE_URL` | Final website origin/custom domain for metadata and sitemap links |
| `NEXT_PUBLIC_PLAY_STORE_URL` | Published Android listing; leave blank until available |
| `NEXT_PUBLIC_MICROSOFT_STORE_URL` | Published Windows listing; leave blank until available |
| `NEXT_PUBLIC_APPLE_STORE_URL` | Published iOS listing; leave blank until available |

Without an explicit site URL, the build uses Vercel's production project URL
or deployment URL. Local builds use `http://localhost:3000`. Changing a public
variable requires a new build. Backend JWT keys, database credentials, Redis
tokens, and wallet keys belong only in the **backend** project.

## 4. Deploy

In the dashboard, import the same repository twice, choose the appropriate
Root Directory, and deploy each project. If prompted, use the settings in the
table above and remove old custom Build/Output overrides on the backend.

Alternatively, with Vercel CLI 48.1.8 or later, run these commands separately
from each project's root directory:

```sh
vercel link
vercel deploy
# After checking the preview and setting production environment variables:
vercel deploy --prod
```

These commands require your own Vercel login and project selection. This
preparation does not create projects, upload secrets, or perform a live deploy.

## 5. Verify the deployment

- Backend `/health` returns `{"status":"ok"}`.
- Backend `/docs` loads, and account registration/sign-in can access the database.
- Website `/tutorial` displays all screenshots; `/sitemap.xml` uses the correct website origin.
- If enabled, `/admin/login` can log in and remain signed in across requests.
- Inspect the backend Cron Jobs/runtime logs for anchoring recovery.
- Keep the API hostname expected by the mobile app (`agal-api.vercel.app` by
  default), or rebuild the APK with `--dart-define=API_BASE_URL=https://your-api.vercel.app`.

Local checks:

```sh
# backend
python -m pytest

# web
npm run lint
npm run build
```
