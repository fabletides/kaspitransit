from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Use SQLite for local development if DATABASE_URL not set
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./kaspitransit.db"  # SQLite for local dev
    )
    SECRET_KEY: str = "super-secret-key-change-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    GEMINI_API_KEY: str = ""
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Authentication modes: 'demo' for hackathon MVP, 'jwt' for production
    AUTH_MODE: str = os.getenv("AUTH_MODE", "demo").lower()
    
    # Development mode: bypass auth for testing
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    SEED_ON_STARTUP: bool = os.getenv("SEED_ON_STARTUP", "false").lower() == "true"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list, handling both comma and JSON formats"""
        origins = self.CORS_ORIGINS
        if isinstance(origins, list):
            return origins
        if origins.startswith("["):
            import json
            return json.loads(origins)
        return [o.strip() for o in origins.split(",")]
    
    @property
    def is_demo_mode(self) -> bool:
        """Returns True if running in demo/hackathon mode"""
        return self.AUTH_MODE == "demo"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
