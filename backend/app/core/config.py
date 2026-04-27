from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    app_name: str = "Document Intelligence Platform"
    app_slug: str = "document intelligence platform"
    app_version: str = "0.1.0"
    environment: str = "development"

    upload_dir : Path = Path("app/storage/uploads")
    extracted_text_dir: Path = Path("app/storage/extracted_text")
    chunk_storage_dir: Path = Path("app/storage/chunks")
    document_index_path: Path = Path("app/storage/documents.json")

    max_upload_size_mb: int = 25

    chunk_size : int = 1000
    chunk_overlap: int = 200
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()

