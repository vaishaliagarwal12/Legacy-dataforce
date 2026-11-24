"""
Security utilities for Legacy DataForce.
Provides CSRF token generation & verification, safe URL validation,
and sanitized error reporting to protect against injection and information disclosure.
"""

import hmac
import logging
import secrets
import functools
from urllib.parse import urlparse
from typing import Optional
from flask import session, current_app, request, redirect, url_for, jsonify
from werkzeug.security import check_password_hash
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


def validate_file_upload(filename: Optional[str], allowed_extensions: Optional[set] = None) -> None:
    """Validates uploaded file extensions (e.g. pdf, doc, docx)."""
    if not filename or not str(filename).strip():
        return
    if allowed_extensions is None:
        allowed_extensions = {"pdf", "doc", "docx", "png", "jpg", "jpeg"}
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in allowed_extensions:
        raise ValidationError(
            f"File extension '.{ext}' is not permitted. Allowed: {', '.join(sorted(allowed_extensions))}"
        )


def is_admin_authenticated() -> bool:
    """Checks whether an administrative session is actively established."""
    if not session.get("admin_logged_in"):
        return False
    expected_user = current_app.config.get("ADMIN_USERNAME", "admin")
    return session.get("admin_user") == expected_user


def authenticate_admin(username: Optional[str], password: Optional[str]) -> bool:
    """Verifies supplied credentials against environment-defined admin account.

    Supports hashed password verification via ADMIN_PASSWORD_HASH as well as
    fallback comparison with ADMIN_PASSWORD.
    """
    if not username or not password:
        return False

    expected_user = current_app.config.get("ADMIN_USERNAME", "admin")
    user_match = hmac.compare_digest(str(username).strip(), str(expected_user).strip())
    if not user_match:
        return False

    admin_hash = current_app.config.get("ADMIN_PASSWORD_HASH")
    if admin_hash and str(admin_hash).strip():
        cleaned_hash = str(admin_hash).strip().strip("'\"")
        pass_match = check_password_hash(cleaned_hash, str(password))
    else:
        expected_pass = current_app.config.get("ADMIN_PASSWORD", "AdminPassword2026!")
        pass_match = hmac.compare_digest(str(password), str(expected_pass))

    if user_match and pass_match:
        session["admin_logged_in"] = True
        session["admin_user"] = expected_user
        session.permanent = True
        return True
    return False


def logout_admin() -> None:
    """Terminates administrative session and purges auth keys."""
    session.pop("admin_logged_in", None)
    session.pop("admin_user", None)
    session.clear()


def admin_required(f):
    """Decorator requiring administrative authentication for web and API endpoints.

    Redirects unauthenticated browser requests to /login.
    Returns HTTP 401 JSON for API and JSON requests.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_authenticated():
            if request.path.startswith("/api/") or (
                request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html
            ):
                return (
                    jsonify(
                        {
                            "status": "fail",
                            "message": "Unauthorized: Admin authentication required.",
                            "code": 401,
                        }
                    ),
                    401,
                )
            next_url = request.full_path if request.query_string else request.path
            return redirect(url_for("auth_bp.login", next=next_url))
        return f(*args, **kwargs)

    decorated_function._admin_required = True
    return decorated_function


