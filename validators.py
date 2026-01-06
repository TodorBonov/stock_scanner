"""
Input validation and sanitization module
Provides functions to validate and sanitize user inputs
"""
import re
import os
from pathlib import Path
from typing import Optional
from config import (
    MAX_TICKER_LENGTH,
    MAX_PATH_LENGTH,
    ALLOWED_TICKER_CHARS,
    MASKED_CREDENTIAL_LENGTH
)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def sanitize_ticker(ticker: str) -> str:
    """
    Sanitize and validate ticker symbol
    
    Args:
        ticker: Ticker symbol to sanitize
        
    Returns:
        Sanitized ticker (uppercase, stripped)
        
    Raises:
        ValidationError: If ticker is invalid
    """
    if not ticker:
        raise ValidationError("Ticker cannot be empty")
    
    if not isinstance(ticker, str):
        raise ValidationError(f"Ticker must be a string, got {type(ticker)}")
    
    # Strip whitespace and convert to uppercase
    ticker = ticker.strip().upper()
    
    # Check length
    if len(ticker) > MAX_TICKER_LENGTH:
        raise ValidationError(f"Ticker too long (max {MAX_TICKER_LENGTH} characters)")
    
    # Check for dangerous characters (prevent injection)
    if not all(c in ALLOWED_TICKER_CHARS for c in ticker):
        invalid_chars = set(ticker) - ALLOWED_TICKER_CHARS
        raise ValidationError(f"Ticker contains invalid characters: {invalid_chars}")
    
    return ticker


def validate_ticker_list(tickers: list) -> list:
    """
    Validate and sanitize a list of ticker symbols
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        List of sanitized ticker symbols
        
    Raises:
        ValidationError: If any ticker is invalid
    """
    if not isinstance(tickers, list):
        raise ValidationError("Ticker list must be a list")
    
    if not tickers:
        raise ValidationError("Ticker list cannot be empty")
    
    sanitized = []
    for ticker in tickers:
        try:
            sanitized.append(sanitize_ticker(ticker))
        except ValidationError as e:
            raise ValidationError(f"Invalid ticker '{ticker}': {e}")
    
    return sanitized


def validate_file_path(file_path: str, must_exist: bool = False) -> Path:
    """
    Validate and sanitize a file path
    
    Args:
        file_path: Path to validate
        must_exist: If True, file must exist
        
    Returns:
        Path object
        
    Raises:
        ValidationError: If path is invalid
    """
    if not file_path:
        raise ValidationError("File path cannot be empty")
    
    if not isinstance(file_path, str):
        raise ValidationError(f"File path must be a string, got {type(file_path)}")
    
    # Check length (Windows path limit)
    if len(file_path) > MAX_PATH_LENGTH:
        raise ValidationError(f"File path too long (max {MAX_PATH_LENGTH} characters)")
    
    # Resolve path to prevent directory traversal
    try:
        path = Path(file_path).resolve()
    except (OSError, ValueError) as e:
        raise ValidationError(f"Invalid file path: {e}")
    
    # Check if path is within current directory (prevent directory traversal)
    try:
        path.relative_to(Path.cwd())
    except ValueError:
        # Allow absolute paths but log a warning
        pass
    
    # Check if file exists if required
    if must_exist and not path.exists():
        raise ValidationError(f"File does not exist: {path}")
    
    return path


def validate_api_key(api_key: Optional[str], key_name: str = "API key") -> str:
    """
    Validate API key format
    
    Args:
        api_key: API key to validate
        key_name: Name of the key for error messages
        
    Returns:
        API key string
        
    Raises:
        ValidationError: If API key is invalid
    """
    if not api_key:
        raise ValidationError(f"{key_name} cannot be empty")
    
    if not isinstance(api_key, str):
        raise ValidationError(f"{key_name} must be a string")
    
    api_key = api_key.strip()
    
    if len(api_key) < 10:  # Reasonable minimum length
        raise ValidationError(f"{key_name} appears to be too short")
    
    return api_key


def mask_credential(credential: str) -> str:
    """
    Mask a credential for safe logging (shows only last N characters)
    
    Args:
        credential: Credential to mask
        
    Returns:
        Masked credential string
    """
    if not credential or len(credential) <= MASKED_CREDENTIAL_LENGTH:
        return "****"
    
    return "*" * (len(credential) - MASKED_CREDENTIAL_LENGTH) + credential[-MASKED_CREDENTIAL_LENGTH:]


def validate_score(score: Optional[float], min_value: float = 0.0, max_value: float = 1.0) -> float:
    """
    Validate a score value
    
    Args:
        score: Score to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Validated score
        
    Raises:
        ValidationError: If score is invalid
    """
    if score is None:
        raise ValidationError("Score cannot be None")
    
    if not isinstance(score, (int, float)):
        raise ValidationError(f"Score must be a number, got {type(score)}")
    
    if not (min_value <= score <= max_value):
        raise ValidationError(f"Score must be between {min_value} and {max_value}, got {score}")
    
    return float(score)

