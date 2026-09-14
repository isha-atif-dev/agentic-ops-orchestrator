"""
Loads configuration and secrets for the app from environment variables.

Centralizing this in one file means every other file just does
`from app.config import settings` instead of each file reading
os.environ directly, which would scatter API-key handling everywhere.
"""

import os
from dotenv import load_dotenv

# Reads the .env file and loads its contents into the environment,
# so os.environ can see them. Only affects local development, in
# Docker the variables come from env_file in docker-compose.yml instead.
load_dotenv()


class Settings:
    """Holds all app-wide configuration values."""
    ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")


settings = Settings()