import httpx
from httpx import RequestError, HTTPStatusError, ConnectError, TimeoutException
import asyncio
from typing import Optional, Any, Dict, Tuple
from datetime import datetime, timedelta


async def fetch_page_content(url: str, timeout: int = 10, retries: int = 3) -> Optional[Tuple[bytes, int, Dict[str, str]]]:
    """
    Fetches the raw content, HTTP status code, and response headers of a web page
    asynchronously with retries and exponential backoff using httpx.

    Returns:
        A tuple of (content_bytes, status_code, headers_dict) if successful (status code 2xx).
        Returns None if fetching fails or if the response is a client/server error (4xx/5xx).
    """
    for attempt in range(retries):
        try:
            # Use httpx.AsyncClient for asynchronous requests
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()  # Raises HTTPStatusError for bad responses (4xx or 5xx)
                return response.content, response.status_code, dict(response.headers)
        except (ConnectError, TimeoutException) as e:
            if attempt < retries - 1:
                sleep_time = 2 ** attempt
                await asyncio.sleep(sleep_time) # Asynchronous sleep
            else:
                return None
        except HTTPStatusError:
            # HTTPStatusError means a 4xx or 5xx response was received.
            # As per previous instructions, this is treated as a failure for content fetching.
            return None
        except RequestError:
            # Catch any other httpx-related exceptions
            return None
    return None


async def get_url_status(url: str, timeout: int = 5, retries: int = 2) -> Optional[int]:
    """
    Retrieves the HTTP status code of a URL asynchronously without downloading the full content.
    Uses HEAD request with retries and exponential backoff.
    """
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.head(url)
                return response.status_code
        except (ConnectError, TimeoutException) as e:
            if attempt < retries - 1:
                sleep_time = 2 ** attempt
                await asyncio.sleep(sleep_time)
            else:
                return None
        except RequestError:
            return None
    return None


class SimpleCache:
    """
    A simple in-memory cache for HTTP request results with a Time To Live (TTL).
    Now stores (content_bytes, status_code, headers) tuples.
    Designed to be compatible with asynchronous usage.
    """
    def __init__(self, ttl: int = 3600):
        self._cache: Dict[str, Tuple[Tuple[bytes, int, Dict[str, str]], datetime]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[Tuple[bytes, int, Dict[str, str]]]:
        """
        Retrieves content (bytes, status_code, headers) from the cache if it's fresh;
        otherwise, returns None.
        """
        if key in self._cache:
            value_tuple, timestamp = self._cache[key]
            if not self._is_expired(timestamp):
                return value_tuple
            else:
                del self._cache[key]  # Remove expired entry
        return None

    def set(self, key: str, value: Tuple[bytes, int, Dict[str, str]]) -> None:
        """
        Adds content (bytes, status_code, headers) to the cache with the current timestamp.
        """
        self._cache[key] = (value, datetime.now())

    def _is_expired(self, timestamp: datetime) -> bool:
        """
        Checks if a cache entry has expired based on its timestamp and the TTL.
        """
        return (datetime.now() - timestamp) > timedelta(seconds=self._ttl)
