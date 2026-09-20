"""
Central application configuration loaded from environment variables (.env).
Keeps ALL secrets and tunables out of source code.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "AI-Powered Intelligent E-Learning Platform"
    SECRET_KEY: str = "insecure-dev-secret-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENV: str = "development"

    DATABASE_URL: str = "sqlite:///./elearning.db"

    LLM_PROVIDER: str = "openai"  # "openai" | "ollama"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    EMBEDDING_PROVIDER: str = "local"  # "local" | "openai"
    LOCAL_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    CHROMA_PERSIST_DIR: str = "./chroma_db"

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 25

    FRONTEND_ORIGIN: str = "http://localhost:5173"


settings = Settings()
