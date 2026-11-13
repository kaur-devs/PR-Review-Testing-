from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost/flagpole"
    admin_token: str = "change-me"
    cache_seconds: int = 30
    max_rules_per_flag: int = 20

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
