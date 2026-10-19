"""Deterministic paper book. Decides; the account manager applies fills."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Optional

from paper.limits import PHI_GATE, propose_size

UNIVERSE: List[Dict[str, Any]] = [
    {"ticker": "wNVDA", "address": "Nv1d1a89xSolanaWrappedAssetPoolx9941", "phi": 91.4, "base": 0.0112},
    {"ticker": "wAAPL", "address": "App1e57xSolanaWrappedAssetPoolx1029", "phi": 89.1, "base": 0.0048},
    {"ticker": "WIF", "address": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "phi": 86.4, "base": 0.0034},
    {"ticker": "BONK", "address": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "phi": 78.2, "base": 0.000021},
    {"ticker": "POPCAT", "address": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", "phi": 61.0, "base": 0.0011},
]


class PaperBook:
    def __init__(self, sol: Mapping[str, Any] | None, take_profit: float = 0.10, stop_loss: float = 0.10):
        self.sol = dict(sol or {})
        self.take_profit = abs(take_profit)
        self.stop_loss = abs(stop_loss)
        self.assets: List[Dict[str, Any]] = [dict(row) for row in UNIVERSE]
        self.prices: Dict[str, float] = {row["ticker"]: float(row["base"]) for row in self.assets}

    def mark(self, step: int) -> None:
        for index, row in enumerate(self.assets):
            ticker = row["ticker"]
            base = float(row["base"])
            wave = math.sin((step + index) / 2.0) * 0.18
            phi = float(row["phi"]) + math.sin(step / 5.0 + index) * 0.4
            phi = max(40.0, min(98.0, phi))
            row["phi"] = round(phi, 2)
            row["price"] = max(1e-8, base * (1.0 + wave))
            self.prices[ticker] = row["price"]

    def decide(
        self,
        step: int,
        balance: float,
        positions: Mapping[str, float],
        entries: Mapping[str, float],
    ) -> Optional[Dict[str, Any]]:
        self.mark(step)
        if positions:
            ticker = next(iter(positions))
            entry = float(entries.get(ticker) or 0)
            now = float(self.prices.get(ticker) or 0)
            if entry <= 0 or now <= 0:
                return None
            ret = (now - entry) / entry
            if ret >= self.take_profit or ret <= -self.stop_loss:
                return {
                    "side": "sell",
                    "symbol": ticker,
                    "size_sol": float(positions[ticker]),
                    "price": now,
                    "return_pct": ret,
                    "reason": "take_profit" if ret >= self.take_profit else "stop_loss",
                }
            return None

        eligible = [row for row in self.assets if float(row["phi"]) >= PHI_GATE]
        if not eligible:
            return None
        pick = max(eligible, key=lambda row: float(row["phi"]))
        size = propose_size(balance, float(pick["phi"]), self.sol)
        if size is None:
            return None
        return {
            "side": "buy",
            "symbol": pick["ticker"],
            "size_sol": size,
            "price": float(pick["price"]),
            "phi": float(pick["phi"]),
            "reason": "phi_gate",
        }
