from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    #  Database
    DB_HOST: str     = "localhost"
    DB_PORT: int     = 5432
    DB_NAME: str     = "doctorzenz"
    DB_USER: str     = "postgres"
    DB_PASSWORD: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

    # JWT
    SECRET_KEY: str                  = "your-secret-key-here"
    ALGORITHM: str                   = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int   = 7

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()