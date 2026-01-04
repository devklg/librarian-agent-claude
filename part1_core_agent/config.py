"""
Configuration Management for Librarian Agent
Uses pydantic-settings for environment variable management
"""

import os
from typing import Optional, List
from pydantic import Field

# Try pydantic-settings first, fall back to pydantic for compatibility
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")

    # Model Configuration
    model_id: str = Field(default="claude-sonnet-4-20250514", env="MODEL_ID")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")

    # Caching
    cache_ttl_seconds: int = Field(default=300, env="CACHE_TTL_SECONDS")
    session_max_age_seconds: int = Field(default=3600, env="SESSION_MAX_AGE_SECONDS")

    # API Server
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=9600, env="API_PORT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    # Security
    cors_origins: str = Field(default="http://localhost:3000", env="CORS_ORIGINS")

    # Database URLs (for future integration)
    chromadb_url: Optional[str] = Field(default=None, env="CHROMADB_URL")
    mongodb_url: Optional[str] = Field(default=None, env="MONGODB_URL")
    neo4j_url: Optional[str] = Field(default=None, env="NEO4J_URL")
    neo4j_user: Optional[str] = Field(default=None, env="NEO4J_USER")
    neo4j_password: Optional[str] = Field(default=None, env="NEO4J_PASSWORD")
    postgres_url: Optional[str] = Field(default=None, env="POSTGRES_URL")

    # Skills
    skills_base_path: str = Field(default="./skills", env="SKILLS_BASE_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if not self.cors_origins:
            return ["http://localhost:3000"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"

    @property
    def has_anthropic_key(self) -> bool:
        """Check if Anthropic API key is configured"""
        return bool(self.anthropic_api_key)

    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(self.openai_api_key)


# Global settings instance
settings = Settings()
