# Agal

Price transparency and harvest traceability for seaweed farmers, traders, and
exporters in Tawi-Tawi.

## Project components

| Directory | Component |
| --- | --- |
| [`apps/agal`](apps/agal) | Flutter mobile app with farmer, supplier, and buyer experiences |
| [`backend`](backend) | FastAPI API, PostgreSQL models and migrations, admin UI, and blockchain anchoring |
| [`contract`](contract) | HarvestLedger Solidity contract and Hardhat tests |
| [`web`](web) | Next.js information site and screenshot tutorial at `/tutorial` |
| [`screenshots`](screenshots) | Feature boards and original captures using demonstration accounts |

## Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for preparing secrets, configuring external
PostgreSQL, and deploying the backend and website as separate Vercel projects.

The backend needs a local `.env` or deployment environment variables. Start
from `backend/.env.example`, then generate local secrets without printing them:

```sh
# From backend, after installing its dependencies:
python scripts/generate_secrets.py
python -m alembic upgrade head
uvicorn app.main:app --reload
```

The mobile app defaults to `https://agal-api.vercel.app`. Override it for local
development with `--dart-define=API_BASE_URL=http://10.0.2.2:8000` on an Android
emulator. See each component's README for full setup instructions.

## Checks

```sh
# backend
python -m pytest

# contract
npm ci
npm test

# web
npm ci
npm run lint
npm run build

# apps/agal
flutter pub get
flutter test
flutter build apk --release
```

## Files kept local

The ignore rules exclude real environment files, signing keys, service-account
credentials, local databases, dependency folders, generated builds/APKs, logs,
and Vercel's machine-specific project-link cache. Only placeholder `.env.example`
and `.env.production.example` templates belong in version control. Configure
Android Maps/signing credentials locally rather than committing them.

Application source, database migrations, dependency lockfiles, contract ABI,
public tutorial images, and the existing app logo/icon assets are included.

Screenshot examples use mock accounts and sample records; they are not live
payments or blockchain transactions.
