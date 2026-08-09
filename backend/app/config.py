"""
Application configuration.

Every value is read from the environment (see .env.example). Nothing here is
hard-coded, and the Euri API key is never committed, logged, or sent to the
frontend.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"), env_file_encoding="utf-8", extra="ignore"
    )

    # --- Euri AI Gateway -----------------------------------------------
    euri_api_key: str = Field(default="", description="Bearer token for api.euron.one")
    euri_base_url: str = Field(default="https://api.euron.one/api/v1/euri")
    euri_generation_model: str = Field(default="gpt-4.1")
    euri_planner_model: str = Field(default="gpt-4.1-mini")
    euri_fallback_model: str = Field(default="gpt-4.1-mini")
    euri_embedding_model: str = Field(default="gemini-embedding-2-preview")
    euri_embedding_dimensions: int = Field(default=1536)

    # --- Vector Database (Qdrant) ----------------------------------------
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant cluster HTTP URL")
    qdrant_api_key: str = Field(default="", description="Qdrant Cloud API Key")

    # --- Supabase / Relational DB (PostgreSQL) ---------------------------
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/ekba",
        description="SQLAlchemy PostgreSQL URL",
    )
    supabase_url: str = Field(default="", description="Supabase project URL")
    supabase_anon_key: str = Field(default="", description="Supabase anon public key")
    supabase_service_role_key: str = Field(
        default="", description="Supabase service role secret key"
    )

    # --- Cache / Rate Limiter (Redis) ------------------------------------
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # --- AWS (S3 & Cognito Auth) -----------------------------------------
    aws_region: str = Field(default="us-east-1")
    aws_access_key_id: str = Field(default="", description="AWS Access Key ID")
    aws_secret_access_key: str = Field(default="", description="AWS Secret Access Key")
    s3_bucket_documents: str = Field(default="ekba-documents-local")
    cognito_user_pool_id: str = Field(default="")
    cognito_app_client_id: str = Field(default="")

    # --- LangSmith Observability ----------------------------------------
    langchain_tracing_v2: str = Field(default="false")
    langchain_api_key: str = Field(default="")
    langchain_project: str = Field(default="ekba-local")

    # --- App -------------------------------------------------------------
    environment: str = Field(default="local")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173")
    max_upload_bytes: int = Field(default=15 * 1024 * 1024)  # 15 MB
    chunk_size_chars: int = Field(default=1200)
    chunk_overlap_chars: int = Field(default=150)
    retrieval_top_k: int = Field(default=6)
    min_similarity_for_answer: float = Field(default=0.15)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
