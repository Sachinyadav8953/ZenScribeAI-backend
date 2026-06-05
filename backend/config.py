
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ── Application ──
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # ── Database (PostgreSQL) ──
    DB_HOST: str        = "localhost"
    DB_PORT: int        = 5432
    DB_NAME: str        = "doctorzenz"
    DB_USER: str        = "postgres"
    DB_PASSWORD: str    = ""

    @property
    def DATABASE_URL(self) -> str:
        # asyncpg — for FastAPI async
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        # psycopg2 — for Alembic migrations only
        return (
            f"postgresql+psycopg2://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

    # ── JWT (Auth) ──
    SECRET_KEY: str                     = "your-secret-key-here"
    ALGORITHM: str                      = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int    = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int      = 7
    PASSWORD_RESET_EXPIRE_MINUTES: int  = 15
    EMAIL_VERIFY_EXPIRE_HOURS: int      = 24

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()