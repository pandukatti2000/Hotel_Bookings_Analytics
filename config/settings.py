import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # App
    APP_NAME: str = "StayWise AI — Hotel Analytics & Intelligence"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    SOURCE_DATA_DIR: Path = BASE_DIR / "hotel_booking-main" / "hotel_booking-main" / "Data"
    CSV_DIR: Path = SOURCE_DATA_DIR / "CSV"
    
    # Primary PostgreSQL Connection
    POSTGRES_USER: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="postgres", validation_alias="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="hotel_bookings_db", validation_alias="POSTGRES_DB")
    DATABASE_URL: str = Field(default="", validation_alias="DATABASE_URL")
    
    # Read-Only PostgreSQL Connection for Safe GenAI
    POSTGRES_READONLY_USER: str = Field(default="hotel_readonly", validation_alias="POSTGRES_READONLY_USER")
    POSTGRES_READONLY_PASSWORD: str = Field(default="ReadOnly@StayWise2026", validation_alias="POSTGRES_READONLY_PASSWORD")
    READONLY_DATABASE_URL: str = Field(default="", validation_alias="READONLY_DATABASE_URL")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", validation_alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    
    # LangSmith
    LANGCHAIN_TRACING_V2: bool = Field(default=False, validation_alias="LANGCHAIN_TRACING_V2")
    LANGCHAIN_ENDPOINT: str = Field(default="https://api.smith.langchain.com", validation_alias="LANGCHAIN_ENDPOINT")
    LANGCHAIN_API_KEY: str = Field(default="", validation_alias="LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = Field(default="staywise-hotel-analytics", validation_alias="LANGCHAIN_PROJECT")

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        from urllib.parse import quote_plus
        pwd = quote_plus(self.POSTGRES_PASSWORD)
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{pwd}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_readonly_database_url(self) -> str:
        if self.READONLY_DATABASE_URL:
            return self.READONLY_DATABASE_URL
        from urllib.parse import quote_plus
        pwd = quote_plus(self.POSTGRES_READONLY_PASSWORD)
        return f"postgresql+psycopg2://{self.POSTGRES_READONLY_USER}:{pwd}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()
