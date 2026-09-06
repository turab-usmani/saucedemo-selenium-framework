"""Centralized configuration module for the test framework.

Reads configuration values from environment variables or a .env file, providing
sensible defaults when environment variables are not explicitly defined.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Automatically load .env file from project root if it exists
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class Config:
    """Application and test execution settings."""

    # Target Web Application URL
    BASE_URL: str = os.getenv("BASE_URL", "https://www.saucedemo.com/").rstrip("/") + "/"

    # Browser settings
    BROWSER: str = os.getenv("BROWSER", "chrome").strip().lower()
    HEADLESS: bool = os.getenv("HEADLESS", "true").strip().lower() in ("true", "1", "yes")

    # Timeouts (in seconds)
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "10"))

    # Demo Credentials
    STANDARD_USER: str = os.getenv("STANDARD_USER", "standard_user")
    LOCKED_OUT_USER: str = os.getenv("LOCKED_OUT_USER", "locked_out_user")
    PROBLEM_USER: str = os.getenv("PROBLEM_USER", "problem_user")
    PASSWORD: str = os.getenv("PASSWORD", "secret_sauce")
