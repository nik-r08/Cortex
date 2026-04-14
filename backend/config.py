from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://cortex:cortex@localhost:5432/cortex"
    database_url_sync: str = "postgresql://cortex:cortex@localhost:5432/cortex"
    redis_url: str = "redis://localhost:6379/0"

    gemini_api_key: str = ""
    groq_api_key: str = ""
    llm_provider: str = "gemini"

    upload_dir: str = "./uploads"
    max_file_size_mb: int = 20

    api_key: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    debug: bool = False
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()
# CORS: configurable origins, default localhost
