from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_API_ENV_FILE,
        frozen=True,
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"
    database_url: str
    supabase_jwt_secret: str | None = None
    supabase_url: str
    supabase_anon_key: str
    jwt_algorithm: Literal["ES256", "HS256"] = "ES256"
    jwt_expiration_hours: int = Field(default=1, gt=0)
    zona_horaria: str = "America/Argentina/Buenos_Aires"
    cors_origins: list[str] = ["http://localhost:3000"]

settings = Settings()