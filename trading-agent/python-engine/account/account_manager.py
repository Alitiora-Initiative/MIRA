"""
Account Manager for Demo/Live trading modes
Handles paper trading simulation and live trading validation
"""

from typing import Dict, Any, Optional
from loguru import logger
from enum import Enum


class AccountMode(Enum):
    DEMO = "demo"
    LIVE = "live"


class AccountManager:
    """Manages demo and live account modes."""

    def __init__(self, config):
        self.config = config
        self.account_mode = AccountMode(config.account_mode.mode)
        self.demo_balance = config.account_mode.demo.get('initial_balance_usd', 10000)
        self.current_balance = self.demo_balance
        self.positions = {}
        self.trades = []

        logger.info(f"Account Manager initialized in {self.account_mode.value} mode")

    def is_demo_mode(self) -> bool:
        """Check if running in demo mode."""
        return self.account_mode == AccountMode.DEMO

    def is_live_mode(self) -> bool:
        """Check if running in live mode."""
        return self.account_mode == AccountMode.LIVE

    def get_balance(self) -> float:
        """Get current account balance."""
        if self.is_demo_mode():
            return self.current_balance
        else:
            # In live mode, balance would come from wallet service
            return 0.0  # Placeholder

    def execute_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Dict[str, Any]:
        """
        Execute a trade (simulated in demo, real in live).

        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            quantity: Trade quantity
            price: Trade price

        Returns:
            Trade result
        """
        if self.is_demo_mode():
            return self._execute_demo_trade(symbol, side, quantity, price)
        else:
            return self._execute_live_trade(symbol, side, quantity, price)

    def _execute_demo_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Dict[str, Any]:
        """Execute simulated trade in demo mode."""
        trade_value = quantity * price

        if side == "buy":
            if trade_value > self.current_balance:
                logger.warning(f"Insufficient balance for buy: {trade_value} > {self.current_balance}")
                return {"success": False, "error": "Insufficient balance"}

            self.current_balance -= trade_value
            self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        else:  # sell
            if symbol not in self.positions or self.positions[symbol] < quantity:
                logger.warning(f"Insufficient position for sell: {symbol}")
                return {"success": False, "error": "Insufficient position"}

            self.current_balance += trade_value
            self.positions[symbol] -= quantity

        trade = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "value": trade_value,
            "timestamp": logger._core.extra_time,
            "mode": "demo"
        }

        self.trades.append(trade)
        logger.info(f"Demo trade executed: {side} {quantity} {symbol} @ {price}")

        return {"success": True, "trade": trade, "balance": self.current_balance}

    def _execute_live_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Dict[str, Any]:
        """Execute real trade in live mode."""
        # In production, this would call the wallet service and exchange manager
        logger.warning(f"Live trade execution not yet implemented: {side} {quantity} {symbol}")
        return {"success": False, "error": "Live trading not yet implemented"}

    def get_positions(self) -> Dict[str, float]:
        """Get current positions."""
        return self.positions.copy()

    def get_trade_history(self) -> list:
        """Get trade history."""
        return self.trades.copy()

    def calculate_pnl(self) -> float:
        """Calculate current P&L (demo mode only)."""
        if self.is_demo_mode():
            return self.current_balance - self.demo_balance
        return 0.0

    def reset_demo_account(self):
        """Reset demo account to initial state."""
        self.current_balance = self.demo_balance
        self.positions = {}
        self.trades = []
        logger.info("Demo account reset")

    def validate_live_trade(
        self,
        symbol: str,
        quantity: float,
        price: float
    ) -> bool:
        """
        Validate trade parameters for live mode.

        Args:
            symbol: Trading symbol
            quantity: Trade quantity
            price: Trade price

        Returns:
            True if trade is valid
        """
        live_config = self.config.account_mode.live

        # Check position size limit
        trade_value = quantity * price
        max_position = live_config.get('max_position_size_usd', 1000)

        if trade_value > max_position:
            logger.warning(f"Trade exceeds max position size: {trade_value} > {max_position}")
            return False

        # Check daily loss limit
        daily_pnl = self.calculate_pnl()
        daily_loss_limit = live_config.get('daily_loss_limit_usd', 100)

        if daily_pnl < -daily_loss_limit:
            logger.warning(f"Daily loss limit reached: {daily_pnl} < -{daily_loss_limit}")
            return False

        return True
