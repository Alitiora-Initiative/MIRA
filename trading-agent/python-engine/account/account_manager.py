"""
Account Manager for paper and live modes.

Paper mode simulates SOL clips. Live mode does not invent fills.
"""

from datetime import datetime, timezone
from typing import Dict, Any
from loguru import logger
from enum import Enum

from paper.limits import bounds, size_allowed


class AccountMode(Enum):
    DEMO = "demo"
    LIVE = "live"


class AccountManager:
    """Manages paper and live account modes."""

    def __init__(self, config):
        self.config = config
        self.account_mode = AccountMode(config.account_mode.mode)
        demo = config.account_mode.demo or {}
        self.paper = self.account_mode == AccountMode.DEMO and bool(demo.get("paper_trading", False))
        if "initial_balance_sol" in demo:
            self.demo_balance = float(demo["initial_balance_sol"])
        else:
            # Legacy configs stored a USD figure here. Do not treat that as SOL.
            self.demo_balance = 25.0
        self.current_balance = self.demo_balance
        self.positions: Dict[str, float] = {}
        self.entries: Dict[str, float] = {}
        self.trades = []
        self.slippage = 0.001 if demo.get("simulate_slippage", True) else 0.0

        logger.info(
            f"Account Manager initialized in {self.account_mode.value} mode "
            f"(paper={self.paper}, bank={self.demo_balance} SOL)"
        )

    def is_demo_mode(self) -> bool:
        return self.account_mode == AccountMode.DEMO

    def is_live_mode(self) -> bool:
        return self.account_mode == AccountMode.LIVE

    def get_balance(self) -> float:
        if self.paper:
            return self.current_balance
        return 0.0

    def _reject_live(self) -> Dict[str, Any]:
        logger.warning("Live order refused. MIRA is in paper-only execution.")
        return {
            "success": False,
            "error": "Live trading is disabled. Start with account_mode.mode=demo and paper_trading=true.",
        }

    def _check_size(self, size_sol: float) -> Dict[str, Any] | None:
        if not size_allowed(size_sol, self.config.trading.sol):
            minimum, maximum = bounds(self.config.trading.sol)
            return {
                "success": False,
                "error": f"Size {size_sol} SOL is outside {minimum}-{maximum} SOL",
            }
        return None

    def execute_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Dict[str, Any]:
        """Execute a paper SOL clip. `quantity` is SOL notional, not a token count."""
        if not self.paper:
            return self._reject_live()
        if side == "buy":
            return self.open_paper(symbol, quantity, price)
        if side == "sell":
            return self.close_paper(symbol, price)
        return {"success": False, "error": "side must be buy or sell"}

    def open_paper(self, symbol: str, size_sol: float, price: float) -> Dict[str, Any]:
        if not self.paper:
            return self._reject_live()
        rejected = self._check_size(size_sol)
        if rejected:
            return rejected
        if price <= 0:
            return {"success": False, "error": "Price must be positive"}
        if symbol in self.positions:
            return {"success": False, "error": "Position already open"}
        if size_sol > self.current_balance + 1e-12:
            return {"success": False, "error": "Insufficient paper SOL"}

        self.current_balance -= size_sol
        self.positions[symbol] = size_sol
        self.entries[symbol] = price
        trade = self._record(symbol, "buy", size_sol, price, size_sol, "open")
        logger.info(f"Paper buy {size_sol} SOL {symbol} @ {price}")
        return {"success": True, "trade": trade, "balance": self.current_balance}

    def close_paper(self, symbol: str, price: float) -> Dict[str, Any]:
        if not self.paper:
            return self._reject_live()
        size_sol = self.positions.get(symbol)
        entry = self.entries.get(symbol)
        if size_sol is None or entry is None or entry <= 0:
            return {"success": False, "error": "No paper position"}
        if price <= 0:
            return {"success": False, "error": "Price must be positive"}

        ret = (price - entry) / entry
        proceeds = size_sol * (1.0 + ret) * (1.0 - self.slippage)
        proceeds = max(0.0, proceeds)
        self.current_balance += proceeds
        del self.positions[symbol]
        del self.entries[symbol]
        trade = self._record(symbol, "sell", size_sol, price, proceeds, "close")
        trade["return_pct"] = ret
        logger.info(f"Paper sell {symbol} ret={ret:.2%} balance={self.current_balance:.6f} SOL")
        return {"success": True, "trade": trade, "balance": self.current_balance, "return_pct": ret}

    def _record(self, symbol: str, side: str, size_sol: float, price: float, value: float, status: str) -> Dict[str, Any]:
        trade = {
            "symbol": symbol,
            "side": side,
            "quantity": size_sol,
            "size_sol": size_sol,
            "price": price,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "paper",
            "status": status,
        }
        self.trades.append(trade)
        return trade

    def get_positions(self) -> Dict[str, float]:
        return self.positions.copy()

    def get_trade_history(self) -> list:
        return self.trades.copy()

    def calculate_pnl(self) -> float:
        if self.paper:
            open_mark = sum(self.positions.values())
            return (self.current_balance + open_mark) - self.demo_balance
        return 0.0

    def reset_demo_account(self):
        self.current_balance = self.demo_balance
        self.positions = {}
        self.entries = {}
        self.trades = []
        logger.info("Paper account reset")

    def validate_live_trade(self, symbol: str, quantity: float, price: float) -> bool:
        """Live validation never approves an order from this process."""
        del symbol, quantity, price
        return False
