from __future__ import annotations

from typing import Any

from app.core.response import ok_response


def admin_ok_response(type: str, **kwargs: Any) -> dict[str, Any]:
    """Return a standardized admin API response.

    Kept intentionally thin so admin route cleanup cannot alter existing response
    envelopes. Admin endpoints pass the same payload/data/meta keys they used to
    pass directly into ok_response.
    """
    return ok_response(type=type, **kwargs)
