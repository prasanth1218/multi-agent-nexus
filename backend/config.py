"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    openai_base_url: str = "https://api.groq.com/openai/v1/"
    # Model Configuration
    planner_model: str = "llama-3.3-70b-versatile"
    agent_model: str = "llama-3.3-70b-versatile"
    reviewer_model: str = "llama-3.3-70b-versatile"
    # Performance
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 500
    max_tokens: int = 4096
    temperature: float = 0.7
    streaming: bool = True
    # Database
    database_path: str = "data/agents.db"
    # Server
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"]
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

def get_settings() -> Settings:
    return Settings()