from dataclasses import dataclass
from typing import Optional

@dataclass
class ErrorCode:
    code: str
    message: str
    details: Optional[str] = None

INVALID_URL = ErrorCode(
    code="E1001",
    message="Invalid URL provided",
    details="URL must start with http:// or https:// and be valid"
)

API_LIMIT_EXCEEDED = ErrorCode(
    code="E2001",
    message="API rate limit exceeded",
    details="Please wait before making additional requests"
)
