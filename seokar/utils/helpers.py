import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import Optional
import tldextract


def is_valid_url(url: str) -> bool:
    """
    Checks if a string is a valid HTTP/HTTPS URL.
    """
    try:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ["http", "https"] and bool(parsed_url.netloc)
    except Exception:
        return False


def clean_html_text(html_content: str) -> str:
    """
    Cleans HTML content to extract readable text, removing tags, scripts,
    styles, and excessive whitespace.
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Get text and clean whitespace
    text = soup.get_text()
    # Replace multiple spaces/newlines/tabs with a single space
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    return cleaned_text


def get_page_size_bytes(content: bytes) -> int:
    """
    Calculates the size of the page content in bytes.
    """
    return len(content)


def convert_bytes_to_kb(bytes_size: int) -> float:
    """
    Converts bytes to kilobytes, rounded to two decimal places.
    """
    return round(bytes_size / 1024, 2)


def extract_domain(url: str) -> Optional[str]:
    """
    Extracts the domain name (e.g., example.com) from a URL using tldextract.
    """
    try:
        extracted = tldextract.extract(url)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        elif extracted.domain: # For cases like 'localhost' or IPs
            return extracted.domain
        return None
    except Exception:
        # Fallback for non-standard URLs or if tldextract fails unexpectedly
        parsed_url = urlparse(url)
        if parsed_url.netloc:
            # Simple approach: remove port and potential userinfo
            netloc_without_port = parsed_url.netloc.split(':')[0].split('@')[-1]
            # This fallback is less robust than tldextract for subdomains etc.
            # but serves as a basic measure if tldextract fails or is not desired.
            return netloc_without_port
        return None
