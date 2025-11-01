"""
Configuration module for Trabajo IA Server.

Manages environment variables and server configuration.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Central configuration class for the MCP server."""

    # FRED API Configuration
    FRED_API_KEY: Optional[str] = os.getenv("FRED_API_KEY")

    # Server Configuration
    SERVER_NAME: str = "trabajo-ia-server"
    SERVER_VERSION: str = "0.1.0"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration values."""
        if not cls.FRED_API_KEY:
            raise ValueError(
                "FRED_API_KEY environment variable is required. "
                "Please set it in your .env file."
            )

    @classmethod
    def get_fred_api_key(cls) -> str:
        """Get FRED API key with validation."""
        if not cls.FRED_API_KEY:
            raise ValueError("FRED_API_KEY not configured")
        return cls.FRED_API_KEY


# Singleton instance
config = Config()
