"""Legacy DataForce - Pagination Parameter Validation and Normalization Helper.

Centralizes pagination logic across routes and controllers, handling non-numeric values,
missing values, negative bounds, whitelist options, and configurable maximum limits.
"""

from typing import Tuple, Optional, Sequence, Any
import logging
from config import Config

logger = logging.getLogger(__name__)


def validate_pagination_params(
    page: Optional[Any] = None,
    per_page: Optional[Any] = None,
    default_page: int = 1,
    default_per_page: Optional[int] = None,
    allowed_per_page: Optional[Sequence[int]] = None,
    max_per_page: Optional[int] = None,
) -> Tuple[int, int]:
    """Validates and normalizes pagination parameters (page and per_page).

    Handles invalid strings, non-numeric values, negative numbers, zero, and out-of-range values.

    Args:
        page: The raw or requested page number.
        per_page: The raw or requested page size.
        default_page: Default page number (default: 1).
        default_per_page: Default items per page (default: Config.DEFAULT_PAGE_SIZE).
        allowed_per_page: Optional whitelist of allowed per_page values (e.g. (10, 25, 50, 100)).
        max_per_page: Upper bound for per_page (default: Config.MAX_PAGE_SIZE).

    Returns:
        Tuple of (clean_page, clean_per_page) guaranteed to be valid positive integers.
    """
    if default_per_page is None:
        default_per_page = getattr(Config, "DEFAULT_PAGE_SIZE", 10)
    if max_per_page is None:
        max_per_page = getattr(Config, "MAX_PAGE_SIZE", 100)

    # 1. Parse and validate page number
    try:
        clean_page = int(page) if page is not None and str(page).strip() != "" else default_page
        if clean_page < 1:
            clean_page = default_page
    except (ValueError, TypeError):
        clean_page = default_page

    # 2. Parse and validate per_page
    try:
        clean_per_page = (
            int(per_page)
            if per_page is not None and str(per_page).strip() != ""
            else default_per_page
        )
        if clean_per_page < 1:
            clean_per_page = default_per_page
    except (ValueError, TypeError):
        clean_per_page = default_per_page

    # 3. Check allowed whitelist if provided
    if allowed_per_page is not None:
        if clean_per_page not in allowed_per_page:
            clean_per_page = default_per_page
    else:
        # Clamp to max_per_page
        if clean_per_page > max_per_page:
            clean_per_page = max_per_page

    return clean_page, clean_per_page
