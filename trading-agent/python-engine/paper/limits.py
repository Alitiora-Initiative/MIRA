"""SOL clip and paper sizing. No network, no keys."""

from __future__ import annotations

import math
from typing import Any, Mapping, Optional, Tuple

MIN_SOL = 0.001
MAX_SOL = 10.0
PHI_GATE = 85.0


def bounds(sol: Mapping[str, Any] | None) -> Tuple[float, float]:
    data = dict(sol or {})
    minimum = float(data.get("min_trade", MIN_SOL))
    maximum = float(data.get("max_trade", MAX_SOL))
    if not math.isfinite(minimum) or not math.isfinite(maximum):
        raise ValueError("SOL bounds must be finite")
    if minimum <= 0 or maximum < minimum:
        raise ValueError(f"invalid SOL bounds min={minimum} max={maximum}")
    return minimum, maximum


def size_allowed(amount: float, sol: Mapping[str, Any] | None) -> bool:
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        return False
    if not math.isfinite(amount) or amount <= 0:
        return False
    minimum, maximum = bounds(sol)
    return (minimum - 1e-12) <= float(amount) <= (maximum + 1e-12)


def propose_size(balance: float, phi: float, sol: Mapping[str, Any] | None) -> Optional[float]:
    """Size a paper clip inside [min, max]. phi 85 -> min, phi >= 98 -> cap."""
    if isinstance(balance, bool) or isinstance(phi, bool):
        return None
    if not isinstance(balance, (int, float)) or not isinstance(phi, (int, float)):
        return None
    if not math.isfinite(balance) or not math.isfinite(phi):
        return None
    if phi < PHI_GATE or balance <= 0:
        return None
    minimum, maximum = bounds(sol)
    if balance < minimum:
        return None
    cap = min(maximum, balance)
    conviction = max(0.0, min(1.0, (phi - PHI_GATE) / 13.0))
    size = minimum + conviction * (cap - minimum)
    size = min(size, cap, maximum)
    size = round(float(size), 9)
    if not size_allowed(size, sol):
        return None
    return size
