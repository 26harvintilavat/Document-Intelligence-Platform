from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Document Intelligence Platform"
    app_slug: str = "document intelligence platform"
    app_version: str = "0.1.0"
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()

