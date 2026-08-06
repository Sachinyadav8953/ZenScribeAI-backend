from pydantic_settings import BaseSettings
from pydantic import Field
from urllib.parse import quote_plus
class Settings(BaseSettings):

    #  Database
    DB_HOST: str     = "localhost"
    DB_PORT: int     = 5432
    DB_NAME: str     = "doctorzenz"
    DB_USER: str     = "postgres"
    DB_PASSWORD: str = ""

    @property
    def DATABASE_URL(self) -> str:
        encoded_password = quote_plus(self.DB_PASSWORD)

        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{encoded_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

    # JWT
    SECRET_KEY: str                  = "your-secret-key-here"
    ALGORITHM: str                   = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int   = 7

    # ── Email ──
    MAIL_USERNAME: str               = ""
    MAIL_PASSWORD: str               = ""
    MAIL_FROM: str                   = "noreply@doctorzenz.com"
    MAIL_FROM_NAME: str              = "Doctor_zenZ"
    MAIL_PORT: int                   = 587
    MAIL_SERVER: str                 = "smtp.gmail.com"
    MAIL_STARTTLS: bool              = True
    MAIL_SSL_TLS: bool               = False
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15

    # ── Deepgram ──
    DEEPGRAM_API_KEY: str            = Field(default="", validation_alias="Deepgram_Key")

    # ── Gemini (LLM) ──
    GEMINI_API_KEY: str              = ""
    GEMINI_MODEL: str                = "gemini-1.5-flash"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()