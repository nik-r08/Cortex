from functools import lru_cache
from pydantic_settings import BaseSettings


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

    def get_async_db_url(self) -> str:
        """Convert standard postgres URL to asyncpg format if needed."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg doesn't understand sslmode param, strip it and use ssl=True
        if "sslmode=" in url:
            url = url.split("?")[0]
        return url

    def get_sync_db_url(self) -> str:
        """Return a standard psycopg2 URL."""
        url = self.database_url_sync or self.database_url
        if "+asyncpg" in url:
            url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url


@lru_cache()
def get_settings() -> Settings:
    return Settings()
