from urllib.parse import urlsplit

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Values shipped in .env.example -- fine on a dev machine, never in production.
_ADMIN_PLACEHOLDERS = {"admin@example.com", "change-this-password", "change-this-secret"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    PROJECT_NAME: str = "Agal API"
    ENVIRONMENT: str = "development"
    VERCEL: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://agal:agal@localhost:5432/agal"

    SECRET_KEY: str = "change-me-to-a-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    CORS_ORIGINS: str = "*"

    # Populated once the Hardhat contract + web3.py integration step lands.
    WEB3_PROVIDER_URL: str | None = None
    HARVEST_LEDGER_ADDRESS: str | None = None
    SERVICE_WALLET_PRIVATE_KEY: str | None = None
    CRON_SECRET: str | None = None

    # Super Admin UI (/admin). Credentials live only in the environment: the
    # admin is deliberately not a row in `users`, so no app account can ever
    # become one. Leaving all three unset disables the admin UI entirely.
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    ADMIN_SESSION_SECRET: str | None = None
    ADMIN_SESSION_IDLE_MINUTES: int = 30
    ADMIN_SESSION_MAX_MINUTES: int = 8 * 60
    UPSTASH_REDIS_REST_URL: str | None = None
    UPSTASH_REDIS_REST_TOKEN: str | None = None

    @property
    def admin_shared_store_enabled(self) -> bool:
        return bool(self.UPSTASH_REDIS_REST_URL and self.UPSTASH_REDIS_REST_TOKEN)

    @property
    def admin_enabled(self) -> bool:
        return bool(self.ADMIN_EMAIL and self.ADMIN_PASSWORD and self.ADMIN_SESSION_SECRET)

    @model_validator(mode="after")
    def _validate_admin(self) -> "Settings":
        if self.VERCEL:
            self.ENVIRONMENT = "production"
            if (not self.DATABASE_URL.startswith(("postgres://", "postgresql://", "postgresql+asyncpg://"))
                    or urlsplit(self.DATABASE_URL).hostname in {None, "localhost", "127.0.0.1", "::1"}):
                raise ValueError("Set DATABASE_URL to an external PostgreSQL database for Vercel")
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "change-me-to-a-random-secret" or len(self.SECRET_KEY) < 32:
                raise ValueError("Set SECRET_KEY to a cryptographically random value of at least 32 characters")
            if self.CRON_SECRET and (self.CRON_SECRET == "change-this-cron-secret" or len(self.CRON_SECRET) < 32):
                raise ValueError("CRON_SECRET must contain at least 32 random characters")
        redis = (self.UPSTASH_REDIS_REST_URL, self.UPSTASH_REDIS_REST_TOKEN)
        if any(redis) and not all(redis):
            raise ValueError("Set both UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN")
        if self.UPSTASH_REDIS_REST_URL and not self.UPSTASH_REDIS_REST_URL.startswith("https://"):
            raise ValueError("UPSTASH_REDIS_REST_URL must use HTTPS")
        values = (self.ADMIN_EMAIL, self.ADMIN_PASSWORD, self.ADMIN_SESSION_SECRET)
        if any(values) and not all(values):
            raise ValueError("ADMIN_EMAIL, ADMIN_PASSWORD and ADMIN_SESSION_SECRET must be set together")
        if self.ENVIRONMENT == "production" and self.admin_enabled:
            if _ADMIN_PLACEHOLDERS & set(values):
                raise ValueError("Admin credentials still use .env.example placeholder values")
            if len(self.ADMIN_PASSWORD or "") < 12:
                raise ValueError("ADMIN_PASSWORD must be at least 12 characters in production")
            if len(self.ADMIN_SESSION_SECRET or "") < 32:
                raise ValueError("ADMIN_SESSION_SECRET must be at least 32 characters in production")
        if self.VERCEL and self.admin_enabled and not self.admin_shared_store_enabled:
            raise ValueError("Admin on Vercel requires shared Upstash Redis sessions; configure Redis or leave the ADMIN credentials unset")
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
