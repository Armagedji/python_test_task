from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Слой конфигурации приложения
    """
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/search_db"
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"
    ELASTICSEARCH_INDEX: str = "documents"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
