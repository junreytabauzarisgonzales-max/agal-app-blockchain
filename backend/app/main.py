from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import auth, batches, cron, custody_events, messages, prices, sync, users
from app.core.config import settings
from app.services.errors import DomainError
from app.admin import NoAdminCORSMiddleware, setup_admin

app = FastAPI(title=settings.PROJECT_NAME)
# production
app.add_middleware(
    NoAdminCORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(prices.router)
app.include_router(batches.router)
app.include_router(custody_events.router)
app.include_router(messages.router)
app.include_router(sync.router)
app.include_router(cron.router)
setup_admin(app)


@app.exception_handler(DomainError)
async def domain_error(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
