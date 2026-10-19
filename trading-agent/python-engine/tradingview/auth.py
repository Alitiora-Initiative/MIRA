"""Constant-time webhook authentication. Fail closed when the key is unset."""

from __future__ import annotations

import hmac
from typing import Optional


def webhook_authorized(presented: Optional[str], expected: Optional[str]) -> bool:
    if not isinstance(presented, str) or not isinstance(expected, str):
        return False
    if not presented or not expected:
        return False
    return hmac.compare_digest(presented.encode("utf-8"), expected.encode("utf-8"))
