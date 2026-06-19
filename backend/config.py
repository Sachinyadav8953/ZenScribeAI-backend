from pydantic_settings import BaseSettings
import os

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



     #Email
   

    MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    MAIL_FROM     = os.environ["MAIL_FROM"]
    MAIL_FROM_NAME    = os.environ["MAIL_FROM"]
    MAIL_PORT: int          = 587
    MAIL_SERVER     = os.environ["MAIL_SERVER"]
    MAIL_STARTTLS: bool   = True
    MAIL_SSL_TLS: bool  = False
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15

    #Deepgram
    DEEPGRAM_API_KEY=os.environ["Deepgram_Key"]

    #gemini

    GEMINI_API_KEY =  os.environ["GEMINI_API_KEY"]
    GEMINI_MODEL   =  os.environ["GEMINI_MODEL"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }




settings = Settings()