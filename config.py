"""
Configuration constants and settings
Centralizes hardcoded values for easier maintenance
"""
from pathlib import Path

# API Rate Limiting
DEFAULT_RATE_LIMIT_DELAY = 0.5  # seconds between API calls
POSITION_EVALUATION_DELAY = 0.5  # seconds between position evaluations
MAX_API_RETRIES = 3

# API Timeouts
TRADING212_API_TIMEOUT = 30  # seconds for Trading212 API calls
OPENAI_API_TIMEOUT = 60  # seconds for OpenAI API calls
DATA_PROVIDER_TIMEOUT = 30  # seconds for data provider API calls

# Score Calculation Weights
TECHNICAL_SCORE_WEIGHT = 0.6
FUNDAMENTAL_SCORE_WEIGHT = 0.4

# Default File Paths
DEFAULT_RULESET_PATH = "ruleset.json"
DEFAULT_ENV_PATH = ".env"
DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "trading212_bot.log"

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Input Validation
MAX_TICKER_LENGTH = 20
MAX_PATH_LENGTH = 260  # Windows path limit
ALLOWED_TICKER_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")

# Security
MASKED_CREDENTIAL_LENGTH = 4  # Show last 4 chars when masking

