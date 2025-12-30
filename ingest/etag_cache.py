"""
ETag Cache Management

Provides utilities for storing and retrieving HTTP ETags to enable
conditional requests and avoid unnecessary data transfers.
"""

import json
import os
from pathlib import Path
from typing import Optional


def load_etags(path: str) -> dict[str, str]:
    """
    Load ETags from a JSON cache file.
    
    Args:
        path: Path to the ETag cache file.
    
    Returns:
        Dictionary mapping URLs to ETag values. Returns empty dict if
        file doesn't exist or is corrupt.
    
    Example:
        >>> etags = load_etags(".cache/chesscom_etags.json")
        >>> print(etags.get("https://api.chess.com/pub/player/user/games/2023/01"))
    """
    if not os.path.exists(path):
        return {}
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except (json.JSONDecodeError, IOError):
        # Corrupt or unreadable file - treat as empty
        return {}


def save_etags(path: str, etags: dict[str, str]) -> None:
    """
    Save ETags to a JSON cache file.
    
    Creates parent directories if they don't exist.
    
    Args:
        path: Path to the ETag cache file.
        etags: Dictionary mapping URLs to ETag values.
    
    Example:
        >>> etags = {"https://api.chess.com/pub/...": "abc123"}
        >>> save_etags(".cache/chesscom_etags.json", etags)
    """
    # Ensure parent directory exists
    parent_dir = Path(path).parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(etags, f, indent=2)


def get_etag(etags: dict[str, str], url: str) -> Optional[str]:
    """
    Retrieve the cached ETag for a URL.
    
    Args:
        etags: Dictionary of cached ETags.
        url: The URL to look up.
    
    Returns:
        The cached ETag string, or None if not found.
    """
    return etags.get(url)


def set_etag(etags: dict[str, str], url: str, etag: str) -> None:
    """
    Store an ETag for a URL in the cache dictionary.
    
    Args:
        etags: Dictionary of cached ETags (modified in place).
        url: The URL to cache.
        etag: The ETag value to store.
    """
    etags[url] = etag
