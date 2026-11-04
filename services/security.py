"""
Security utilities for Legacy DataForce.
Provides CSRF token generation & verification, safe URL validation,
and sanitized error reporting to protect against injection and information disclosure.
"""

import hmac
import logging
import secrets
from urllib.parse import urlparse
from typing import Optional
from flask import session
from services.exceptions import ValidationError

logger = logging.getLogger(__name__)


def generate_csrf_token() -> str:
    """Generates a cryptographically secure CSRF token tied to the user's session.

    If the session does not yet have a token, one is generated and stored.
    """
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def verify_csrf_token(token: Optional[str]) -> bool:
    """Verifies that the provided CSRF token matches the active session token using constant-time comparison."""
    expected = session.get("_csrf_token")
    if not expected or not token:
        return False
    return hmac.compare_digest(str(token).strip(), str(expected).strip())


def validate_safe_url(url: Optional[str], field_name: str = "URL") -> None:
    """Validates that a URL uses safe protocols (http or https) to prevent stored XSS attacks
    such as 'javascript:' or 'data:' URI schemes.

    Raises:
        ValidationError if an unsafe scheme or malformed URL is detected.
    """
    if not url or not str(url).strip():
        return

    cleaned = str(url).strip()
    parsed = urlparse(cleaned)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValidationError(
            f"Invalid {field_name}: Only secure HTTP/HTTPS URLs are allowed (e.g., https://example.com)."
        )
