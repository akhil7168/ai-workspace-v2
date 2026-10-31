from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str

    DATABASE_URL: str

    SECRET_KEY: str

    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int

    REFRESH_TOKEN_EXPIRE_DAYS: int

    ENVIRONMENT: str = "development"
    REPOSITORY_CLONE_TIMEOUT_SECONDS: int = 120
    REPOSITORY_MAX_FILE_BYTES: int = 1_000_000
    REPOSITORY_MAX_FILES: int = 20_000
    REPOSITORY_MAX_TOTAL_BYTES: int = 100_000_000
    REPOSITORY_MAX_PROCESSING_SECONDS: int = 120
    CODE_CHUNK_MAX_CHARS: int = 8000
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_AUTO_GENERATE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()