import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
import time
from typing import Optional, Any, Dict, Tuple
from datetime import datetime, timedelta


def fetch_page_content(url: str, timeout: int = 10, retries: int = 3) -> Optional[bytes]:
    """
    Fetches the raw content of a web page (as bytes) with retries and exponential backoff.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            return response.content
        except (ConnectionError, Timeout) as e:
            if attempt < retries - 1:
                sleep_time = 2 ** attempt
                # print(f"Connection/Timeout error for {url}: {e}. Retrying in {sleep_time} seconds...") # For debugging purposes
                time.sleep(sleep_time)
            else:
                # print(f"Final Connection/Timeout error for {url}: {e}") # For debugging purposes
                return None
        except HTTPError as e:
            # print(f"HTTP error for {url}: {e.response.status_code} - {e.response.reason}") # For debugging purposes
            return None
        except RequestException as e:
            # print(f"An unexpected request error occurred for {url}: {e}") # For debugging purposes
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
                # print(f"Connection/Timeout error for HEAD {url}: {e}. Retrying in {sleep_time} seconds...") # For debugging purposes
                time.sleep(sleep_time)
            else:
                # print(f"Final Connection/Timeout error for HEAD {url}: {e}") # For debugging purposes
                return None
        except RequestException as e:
            # print(f"An unexpected request error occurred for HEAD {url}: {e}") # For debugging purposes
            return None
    return None


class SimpleCache:
    """
    A simple in-memory cache for HTTP request results with a Time To Live (TTL).
    """
    def __init__(self, ttl: int = 3600):
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves content from the cache if it's fresh; otherwise, returns None.
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            if not self._is_expired(timestamp):
                return value
            else:
                del self._cache[key]  # Remove expired entry
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Adds content to the cache with the current timestamp.
        """
        self._cache[key] = (value, datetime.now())

    def _is_expired(self, timestamp: datetime) -> bool:
        """
        Checks if a cache entry has expired based on its timestamp and the TTL.
        """
        return (datetime.now() - timestamp) > timedelta(seconds=self._ttl)
