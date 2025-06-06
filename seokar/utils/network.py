import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
import time
from typing import Optional, Any, Dict, Tuple
from datetime import datetime, timedelta


def fetch_page_content(url: str, timeout: int = 10, retries: int = 3) -> Optional[Tuple[bytes, int, Dict[str, str]]]:
    """
    Fetches the raw content, HTTP status code, and response headers of a web page
    with retries and exponential backoff.

    Returns:
        A tuple of (content_bytes, status_code, headers_dict) if successful (status code 2xx).
        Returns None if fetching fails or if the response is a client/server error (4xx/5xx).
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            return response.content, response.status_code, dict(response.headers)
        except (ConnectionError, Timeout) as e:
            if attempt < retries - 1:
                sleep_time = 2 ** attempt
                time.sleep(sleep_time)
            else:
                return None
        except HTTPError:
            # HTTPError means a 4xx or 5xx response was received, which is not considered "successful"
            # for content fetching purposes, so return None as per instructions.
            return None
        except RequestException:
            # Catch any other requests-related exceptions
            return None
    return None


def get_url_status(url: str, timeout: int = 5, retries: int = 2) -> Optional[int]:
    """
    Retrieves the HTTP status code of a URL without downloading the full content.
    Uses HEAD request with retries and exponential backoff.
    """
    for attempt in range(retries):
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code
        except (ConnectionError, Timeout) as e:
            if attempt < retries - 1:
                sleep_time = 2 ** attempt
                time.sleep(sleep_time)
            else:
                return None
        except RequestException as e:
            return None
    return None


class SimpleCache:
    """
    A simple in-memory cache for HTTP request results with a Time To Live (TTL).
    Now stores (content_bytes, status_code, headers) tuples.
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
