import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException
from datetime import datetime, timedelta
import time # Needed for time.sleep mocking

from seokar.utils.network import fetch_page_content, get_url_status, SimpleCache
from seokar.constants.core import StatusCode


@pytest.fixture
def mock_requests_get():
    """Fixture to mock requests.get."""
    with patch('requests.get') as mock_get:
        # Default mock response for success
        mock_response = MagicMock()
        mock_response.content = b"Mock HTML Content"
        mock_response.status_code = StatusCode.OK
        mock_response.headers = {"Content-Type": "text/html", "X-Custom-Header": "Value"}
        mock_response.raise_for_status.return_value = None # Doesn't raise by default
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_head():
    """Fixture to mock requests.head."""
    with patch('requests.head') as mock_head:
        mock_response = MagicMock()
        mock_response.status_code = StatusCode.OK
        mock_head.return_value = mock_response
        yield mock_head


@pytest.fixture
def fixed_datetime_now():
    """Fixture to mock datetime.now() for predictable time in tests."""
    with patch('seokar.utils.network.datetime') as mock_dt:
        # Ensure that datetime.now() returns a fixed time, but datetime.timedelta works normally
        mock_dt.now.return_value = datetime(2023, 1, 1, 10, 0, 0)
        mock_dt.timedelta = timedelta # Ensure timedelta remains original
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs) # Allow real datetime construction if needed
        yield mock_dt


# --- fetch_page_content Tests ---

def test_fetch_page_content_success(mock_requests_get):
    """Test fetch_page_content returns content, status, and headers on success."""
    url = "http://example.com/success"
    content, status, headers = fetch_page_content(url)

    assert content == b"Mock HTML Content"
    assert status == StatusCode.OK
    assert headers == {"Content-Type": "text/html", "X-Custom-Header": "Value"}
    mock_requests_get.assert_called_once_with(url, timeout=10, allow_redirects=True)
    mock_requests_get.return_value.raise_for_status.assert_called_once()


@pytest.mark.parametrize("status_code", [StatusCode.NOT_FOUND, StatusCode.INTERNAL_SERVER_ERROR])
def test_fetch_page_content_http_error(mock_requests_get, status_code):
    """Test fetch_page_content returns None for 4xx/5xx HTTP errors."""
    url = f"http://example.com/error_{status_code}"
    
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.raise_for_status.side_effect = HTTPError(response=mock_response) # Simulate raising HTTPError
    mock_requests_get.return_value = mock_response

    result = fetch_page_content(url)
    assert result is None
    mock_requests_get.assert_called_once_with(url, timeout=10, allow_redirects=True)
    mock_requests_get.return_value.raise_for_status.assert_called_once()


@patch('time.sleep', return_value=None) # Mock time.sleep to speed up tests
def test_fetch_page_content_connection_error_with_retries(mock_sleep, mock_requests_get):
    """Test fetch_page_content retries on ConnectionError and eventually succeeds."""
    url = "http://example.com/retry"
    
    # Simulate 2 ConnectionErrors then success
    mock_requests_get.side_effect = [
        ConnectionError,
        ConnectionError,
        mock_requests_get.return_value # Original successful mock response
    ]

    content, status, headers = fetch_page_content(url, retries=3)

    assert content == b"Mock HTML Content"
    assert status == StatusCode.OK
    assert mock_requests_get.call_count == 3
    # Check sleep calls, exponential backoff (1s, 2s)
    mock_sleep.assert_any_call(1)
    mock_sleep.assert_any_call(2)


@patch('time.sleep', return_value=None)
def test_fetch_page_content_connection_error_exhausts_retries(mock_sleep, mock_requests_get):
    """Test fetch_page_content returns None when ConnectionError persists."""
    url = "http://example.com/no-retry"
    
    # Simulate 3 ConnectionErrors (all retries fail)
    mock_requests_get.side_effect = ConnectionError

    result = fetch_page_content(url, retries=3)

    assert result is None
    assert mock_requests_get.call_count == 3
    mock_sleep.assert_any_call(1)
    mock_sleep.assert_any_call(2) # Only two sleeps for 3 attempts


@patch('time.sleep', return_value=None)
def test_fetch_page_content_timeout_error(mock_sleep, mock_requests_get):
    """Test fetch_page_content handles Timeout errors with retries."""
    url = "http://example.com/timeout"
    
    # Simulate 1 Timeout then success
    mock_requests_get.side_effect = [
        Timeout,
        mock_requests_get.return_value
    ]

    content, status, headers = fetch_page_content(url, retries=2)

    assert content == b"Mock HTML Content"
    assert status == StatusCode.OK
    assert mock_requests_get.call_count == 2
    mock_sleep.assert_called_once_with(1)


def test_fetch_page_content_unexpected_request_exception(mock_requests_get):
    """Test fetch_page_content returns None for general RequestException."""
    url = "http://example.com/general-error"
    mock_requests_get.side_effect = RequestException("Something went wrong")

    result = fetch_page_content(url, retries=1) # No retries for general errors

    assert result is None
    mock_requests_get.assert_called_once()


# --- get_url_status Tests ---

def test_get_url_status_success(mock_requests_head):
    """Test get_url_status returns status code on success."""
    url = "http://example.com/status"
    mock_requests_head.return_value.status_code = StatusCode.OK
    
    status = get_url_status(url)
    assert status == StatusCode.OK
    mock_requests_head.assert_called_once_with(url, timeout=5, allow_redirects=True)


def test_get_url_status_404_status(mock_requests_head):
    """Test get_url_status returns 404 status code."""
    url = "http://example.com/404"
    mock_requests_head.return_value.status_code = StatusCode.NOT_FOUND
    
    status = get_url_status(url)
    assert status == StatusCode.NOT_FOUND
    mock_requests_head.assert_called_once_with(url, timeout=5, allow_redirects=True)


@patch('time.sleep', return_value=None)
def test_get_url_status_connection_error_with_retries(mock_sleep, mock_requests_head):
    """Test get_url_status retries on ConnectionError and eventually succeeds."""
    url = "http://example.com/status-retry"
    
    # Simulate 1 ConnectionError then success
    mock_requests_head.side_effect = [
        ConnectionError,
        mock_requests_head.return_value # Original successful mock response
    ]

    status = get_url_status(url, retries=2)

    assert status == StatusCode.OK
    assert mock_requests_head.call_count == 2
    mock_sleep.assert_called_once_with(1)


@patch('time.sleep', return_value=None)
def test_get_url_status_exhausts_retries(mock_sleep, mock_requests_head):
    """Test get_url_status returns None when ConnectionError persists."""
    url = "http://example.com/status-no-retry"
    
    # Simulate 2 ConnectionErrors (all retries fail)
    mock_requests_head.side_effect = ConnectionError

    status = get_url_status(url, retries=2)

    assert status is None
    assert mock_requests_head.call_count == 2
    mock_sleep.assert_called_once_with(1)


# --- SimpleCache Tests ---

def test_simple_cache_set_and_get():
    """Test that SimpleCache can set and retrieve values."""
    cache = SimpleCache(ttl=1) # Short TTL for potential later tests
    key = "test_key"
    value = (b"some content", 200, {"header": "val"})
    
    cache.set(key, value)
    retrieved_value = cache.get(key)
    
    assert retrieved_value == value


def test_simple_cache_get_expired(fixed_datetime_now):
    """Test that SimpleCache returns None for expired entries."""
    cache = SimpleCache(ttl=5) # 5 second TTL
    key = "expired_key"
    value = (b"expired content", 200, {})
    
    cache.set(key, value)
    
    # Advance time beyond TTL
    fixed_datetime_now.now.return_value += timedelta(seconds=6)
    
    retrieved_value = cache.get(key)
    
    assert retrieved_value is None
    # Check that the item is removed from the cache
    assert key not in cache._cache


def test_simple_cache_get_not_expired(fixed_datetime_now):
    """Test that SimpleCache returns the value for non-expired entries."""
    cache = SimpleCache(ttl=10) # 10 second TTL
    key = "non_expired_key"
    value = (b"fresh content", 200, {})
    
    cache.set(key, value)
    
    # Advance time within TTL
    fixed_datetime_now.now.return_value += timedelta(seconds=5)
    
    retrieved_value = cache.get(key)
    
    assert retrieved_value == value
    # Check that the item is still in the cache
    assert key in cache._cache


def test_simple_cache_different_keys():
    """Test that SimpleCache handles multiple distinct keys correctly."""
    cache = SimpleCache()
    key1 = "key_one"
    value1 = (b"content 1", 200, {})
    key2 = "key_two"
    value2 = (b"content 2", 404, {"error": "true"})

    cache.set(key1, value1)
    cache.set(key2, value2)

    assert cache.get(key1) == value1
    assert cache.get(key2) == value2

    # Ensure getting non-existent key returns None
    assert cache.get("non_existent_key") is None
