from typing import Any, Dict
from urllib.parse import urlparse

def clean_url(url: str) -> str:
    """Normalize URL by removing query parameters and fragments"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def safe_get(data: Dict[str, Any], *keys: str) -> Any:
    """Safely get nested dictionary keys"""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current
