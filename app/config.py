from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Postgres DB
    db_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/spimex_db"
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_reset_hour: int = 14
    cache_reset_minute: int = 11


settings = Settings()
