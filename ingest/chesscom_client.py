"""
Chess.com API Client

Provides a robust, production-grade client for fetching chess game data
from the Chess.com public API with retry logic, rate limiting, and ETag support.
"""

import os
import random
import time
from typing import Optional

import requests


class ChessComClientError(Exception):
    """Base exception for Chess.com client errors."""
    pass


class ChessComAPIError(ChessComClientError):
    """Raised when the Chess.com API returns an error response."""
    
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"Chess.com API error {status_code}: {message}")


class ChessComClient:
    """
    Client for interacting with the Chess.com public API.
    
    Implements robust HTTP behavior including:
    - Exponential backoff with jitter for transient errors
    - Rate limit handling with Retry-After support
    - ETag support for conditional requests (304 Not Modified)
    - Configurable timeouts and retry limits
    
    Args:
        user_agent: User-Agent header value. Defaults to CHESSBI_USER_AGENT env var
                   or "ChessBI (contact: unknown)" if not set.
        timeout_seconds: Request timeout in seconds. Default: 30.
        max_retries: Maximum number of retry attempts. Default: 5.
        backoff_base_seconds: Base delay for exponential backoff. Default: 1.0.
    
    Example:
        >>> client = ChessComClient(user_agent="ChessBI (contact: user@example.com)")
        >>> archives = client.get_archives("hikaru")
        >>> status, data, etag = client.get_month_archive(archives[0])
    """
    
    BASE_URL = "https://api.chess.com/pub"
    
    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout_seconds: int = 30,
        max_retries: int = 5,
        backoff_base_seconds: float = 1.0,
    ):
        """Initialize the Chess.com API client."""
        self.user_agent = user_agent or os.getenv(
            "CHESSBI_USER_AGENT",
            "ChessBI (contact: unknown)"
        )
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_base_seconds = backoff_base_seconds
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        })
    
    def get_archives(self, username: str) -> list[str]:
        """
        Retrieve list of monthly game archive URLs for a player.
        
        Args:
            username: Chess.com username.
        
        Returns:
            List of archive URLs (e.g., ["https://api.chess.com/pub/player/.../2023/01"]).
        
        Raises:
            ChessComAPIError: If the API returns a non-retryable error.
            ChessComClientError: If the response format is invalid.
        """
        url = f"{self.BASE_URL}/player/{username}/games/archives"
        response = self._request_with_retry("GET", url)
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise ChessComClientError(f"Invalid JSON response from {url}: {e}")
        
        if not isinstance(data, dict) or "archives" not in data:
            raise ChessComClientError(
                f"Unexpected response format from {url}: missing 'archives' field"
            )
        
        archives = data["archives"]
        if not isinstance(archives, list):
            raise ChessComClientError(
                f"Unexpected response format: 'archives' is not a list"
            )
        
        return archives
    
    def get_month_archive(
        self,
        url: str,
        etag: Optional[str] = None
    ) -> tuple[int, Optional[dict], Optional[str]]:
        """
        Fetch a monthly game archive with optional ETag support.
        
        Supports conditional requests: if the provided ETag matches the server's
        current version, returns 304 Not Modified to avoid redundant data transfer.
        
        Args:
            url: Full URL to the monthly archive endpoint.
            etag: Optional ETag from previous request for conditional fetch.
        
        Returns:
            Tuple of (status_code, json_data_or_none, new_etag_or_none):
            - status_code: HTTP status code (200, 304, etc.)
            - json_data: Parsed JSON data if status is 200, else None
            - etag: New ETag header value if present, else None
        
        Raises:
            ChessComAPIError: If the API returns a non-retryable error.
        
        Example:
            >>> status, data, new_etag = client.get_month_archive(url, old_etag)
            >>> if status == 304:
            ...     print("Not modified, use cached data")
            >>> elif status == 200:
            ...     print(f"New data with {len(data['games'])} games")
        """
        headers = {}
        if etag:
            # Conditional request: server returns 304 if content unchanged
            headers["If-None-Match"] = etag
        
        response = self._request_with_retry("GET", url, headers=headers, allow_304=True)
        
        status_code = response.status_code
        new_etag = response.headers.get("ETag")
        
        if status_code == 304:
            # Not modified - use cached data
            return (304, None, new_etag)
        
        # Status is 200 - parse new data
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise ChessComClientError(f"Invalid JSON response from {url}: {e}")
        
        return (status_code, data, new_etag)
    
    def _request_with_retry(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        allow_304: bool = False
    ) -> requests.Response:
        """
        Execute HTTP request with exponential backoff retry logic.
        
        Retry behavior:
        - 429 (rate limit): Retry with Retry-After header or exponential backoff
        - 5xx (server error): Retry with exponential backoff
        - 4xx (client error): No retry (except 429)
        - Network errors (timeout, connection): Retry with exponential backoff
        
        Args:
            method: HTTP method (GET, POST, etc.).
            url: Target URL.
            headers: Optional additional headers.
            allow_304: If True, don't raise exception for 304 status.
        
        Returns:
            Successful response object.
        
        Raises:
            ChessComAPIError: For non-retryable client errors.
            ChessComClientError: For exhausted retries or connection issues.
        """
        request_headers = headers or {}
        attempt = 0
        
        while attempt <= self.max_retries:
            try:
                response = self.session.request(
                    method,
                    url,
                    headers=request_headers,
                    timeout=self.timeout_seconds
                )
                
                # Handle 304 Not Modified
                if response.status_code == 304 and allow_304:
                    return response
                
                # Handle rate limiting (429)
                # Handle rate limiting (429) - respect Retry-After header
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            sleep_seconds = int(retry_after)
                        except ValueError:
                            # Retry-After might be an HTTP date, fall back to backoff
                            sleep_seconds = self._calculate_backoff(attempt)
                    else:
                        sleep_seconds = self._calculate_backoff(attempt)
                    
                    if attempt < self.max_retries:
                        time.sleep(sleep_seconds)
                        attempt += 1
                        continue
                    else:
                        raise ChessComAPIError(
                            429,
                            f"Rate limit exceeded after {self.max_retries} retries"
                        )
                
                # Handle server errors (5xx) - transient, retry
                if 500 <= response.status_code < 600:
                    if attempt < self.max_retries:
                        sleep_seconds = self._calculate_backoff(attempt)
                        time.sleep(sleep_seconds)
                        attempt += 1
                        continue
                    else:
                        raise ChessComAPIError(
                            response.status_code,
                            f"Server error after {self.max_retries} retries"
                        )
                
                # Handle client errors (4xx) - permanent, don't retry (except 429)
                if 400 <= response.status_code < 500:
                    raise ChessComAPIError(
                        response.status_code,
                        f"Client error: {response.text[:200]}"
                    )
                
                # Success (2xx)
                if 200 <= response.status_code < 300:
                    return response
                
                # Unexpected status code
                raise ChessComAPIError(
                    response.status_code,
                    f"Unexpected status code: {response.text[:200]}"
                )
            
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                # Transient network errors - retry with backoff
                if attempt < self.max_retries:
                    sleep_seconds = self._calculate_backoff(attempt)
                    time.sleep(sleep_seconds)
                    attempt += 1
                    continue
                else:
                    raise ChessComClientError(
                        f"Network error after {self.max_retries} retries: {e}"
                    )
            
            except requests.exceptions.RequestException as e:
                # Other request errors - permanent, don't retry
                raise ChessComClientError(f"Request failed: {e}")
        
        # Should not reach here, but just in case
        raise ChessComClientError(f"Max retries ({self.max_retries}) exhausted")
    
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Formula: delay = base * 2^attempt + jitter
        Jitter: ±25% randomization to prevent thundering herd
        
        Args:
            attempt: Current retry attempt number (0-indexed).
        
        Returns:
            Sleep duration in seconds.
        """
        # Exponential backoff: base * 2^attempt
        delay = self.backoff_base_seconds * (2 ** attempt)
        
        # Add jitter: ±25% randomization to avoid synchronized retries
        jitter = delay * 0.25 * (2 * random.random() - 1)
        
        return delay + jitter
    
    def close(self):
        """Close the underlying HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
