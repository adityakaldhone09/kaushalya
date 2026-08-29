from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "KAUSHALYA"
    ENVIRONMENT: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/kaushalya_db"
    MONGODB_DB_NAME: str = "kaushalya_db"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # LLM
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # AI limits
    AI_MAX_MESSAGE_LENGTH: int = 4000
    AI_MAX_CONTEXT_DOCUMENTS: int = 8

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def allowed_origins(self) -> list[str]:
        origins = [self.FRONTEND_URL]
        if self.is_development:
            origins += [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
            ]
        return list(set(origins))


@lru_cache()
def get_settings() -> Settings:
    return Settings()
