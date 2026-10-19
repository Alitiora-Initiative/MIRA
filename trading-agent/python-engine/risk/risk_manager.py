"""
Risk Manager - Continuous-time calculus based risk management.
"""

from typing import Dict, List, Any
from loguru import logger
from dataclasses import dataclass
import time

from core.config import Config
from paper.limits import size_allowed, bounds


@dataclass
class Position:
    """Position tracking with continuous-time calculus parameters."""
    position_id: str
    token_address: str
    entry_price: float
    current_price: float
    entry_time: float
    amount: float
    side: str


class RiskManager:
    """Manages trading risk with continuous-time calculus parameters."""

    def __init__(self, config: Config):
        self.config = config
        self.daily_pnl = 0.0
        self.equity_basis = 0.0
        self.current_positions: Dict[str, Position] = {}
        self.risk_config = config.risk_management
        logger.info("Risk Manager initialized")

    def set_equity_basis(self, equity_sol: float) -> None:
        self.equity_basis = max(0.0, float(equity_sol))

    async def evaluate_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate trading signals against risk criteria."""
        approved_signals = []

        for signal in signals:
            try:
                if await self._check_signal_risk(signal):
                    approved_signals.append(signal)
                else:
                    logger.info(f"Signal rejected by risk manager: {signal.get('token_address', signal.get('symbol', 'unknown'))}")

            except Exception as e:
                logger.error(f"Error evaluating signal: {e}")

        return approved_signals

    async def _check_signal_risk(self, signal: Dict[str, Any]) -> bool:
        """Check if a signal meets risk criteria."""
        loss_limit = self.config.trading.max_daily_loss
        if 0 < loss_limit <= 1 and self.equity_basis > 0:
            if self.daily_pnl < -(loss_limit * self.equity_basis):
                logger.warning("Daily loss limit reached, rejecting signal")
                return False
        elif self.daily_pnl < -abs(loss_limit):
            logger.warning("Daily loss limit reached, rejecting signal")
            return False

        if len(self.current_positions) >= self.config.trading.max_open_positions:
            logger.warning("Max open positions reached, rejecting signal")
            return False

        amount = float(signal.get("amount") or 0)
        if not size_allowed(amount, self.config.trading.sol):
            minimum, maximum = bounds(self.config.trading.sol)
            logger.warning(f"SOL size {amount} outside {minimum}-{maximum}")
            return False

        if amount > self.config.trading.max_position_size:
            logger.warning("Position size exceeds limit, rejecting signal")
            return False

        confidence = signal.get("confidence", 0)
        min_confidence = 0.5
        if confidence < min_confidence:
            logger.warning(f"Signal confidence too low: {confidence}")
            return False

        return True

    async def evaluate_arbitrage(self, opportunity: Dict[str, Any]) -> bool:
        """Reject arbitrage unless an explicit minimum profit is configured.

        There is no strategies.arbitrage block on Config. Missing config used
        to raise AttributeError and could fail open in a caller that ignored
        the exception. This fails closed.
        """
        configured = getattr(self.config, "strategies", None)
        if not configured:
            logger.warning("Arbitrage disabled: no strategy config")
            return False
        min_profit = float(configured.get("arbitrage", {}).get("min_profit_percentage", 0)) / 100
        profit = float(opportunity.get("profit_percentage") or 0)
        return profit >= min_profit and min_profit > 0

    def _position_value(self, position: Position) -> float:
        return float(position.amount) * float(position.current_price)

    async def check_portfolio_risk(self):
        """Check overall portfolio risk."""
        try:
            values = [self._position_value(pos) for pos in self.current_positions.values()]
            total_exposure = sum(values)
            max_single_position = max(values, default=0)

            if total_exposure > 0:
                concentration = max_single_position / total_exposure
                if concentration > self.config.risk_management.diversification_threshold:
                    logger.warning(f"Portfolio concentration too high: {concentration:.2%}")

        except Exception as e:
            logger.error(f"Error checking portfolio risk: {e}")

    async def check_positions(self):
        """Check individual positions for risk using continuous-time calculus."""
        for position_id, position in list(self.current_positions.items()):
            try:
                pt = position.current_price
                p0 = position.entry_price
                if p0 <= 0:
                    logger.warning(f"Skipping position {position_id}: entry price is not positive")
                    continue

                price_change_pct = (pt - p0) / p0

                if price_change_pct <= self.risk_config.stop_loss_ceiling:
                    logger.info(f"Stop loss ceiling triggered for position {position_id}: {price_change_pct:.2%}")
                    await self._close_position(position_id, "stop_loss_ceiling")
                    continue

                if price_change_pct <= self.risk_config.stop_loss_floor:
                    logger.info(f"Stop loss floor triggered for position {position_id}: {price_change_pct:.2%}")
                    await self._close_position(position_id, "stop_loss_floor")
                    continue

                if price_change_pct >= self.risk_config.take_profit_cap:
                    logger.info(f"Take profit cap triggered for position {position_id}: {price_change_pct:.2%}")
                    await self._close_position(position_id, "take_profit_cap")
                    continue

                if price_change_pct >= self.risk_config.take_profit_floor:
                    logger.info(f"Take profit floor triggered for position {position_id}: {price_change_pct:.2%}")
                    await self._close_position(position_id, "take_profit_floor")

            except Exception as e:
                logger.error(f"Error checking position {position_id}: {e}")

    async def _close_position(self, position_id: str, reason: str) -> bool:
        """Drop a position from the risk book. Does not broadcast a live swap."""
        try:
            position = self.current_positions.get(position_id)
            if not position:
                return False

            logger.info(f"Closing paper risk position {position_id}: {reason}")
            self.remove_position(position_id)
            return True

        except Exception as e:
            logger.error(f"Error closing position {position_id}: {e}")
            return False

    def calculate_position_size(
        self,
        signal: Dict[str, Any],
        portfolio_value: float
    ) -> float:
        """Calculate optimal position size, then hard-clip to the SOL band."""
        method = self.config.risk_management.position_sizing_method
        minimum, maximum = bounds(self.config.trading.sol)

        if method == "fixed":
            size = portfolio_value * min(self.config.trading.max_position_size, 1.0)
        elif method == "kelly_criterion":
            win_rate = signal.get("win_rate", 0.5)
            avg_win = signal.get("avg_win", 0.05)
            avg_loss = signal.get("avg_loss", 0.03)
            if avg_win <= 0:
                size = minimum
            else:
                kelly_pct = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
                kelly_pct = max(0, min(kelly_pct, 0.25))
                size = portfolio_value * kelly_pct
        elif method == "risk_parity":
            slots = max(1, self.config.trading.max_open_positions)
            size = portfolio_value / slots
        else:
            size = portfolio_value * 0.02

        if size < minimum:
            return 0.0
        return min(size, maximum, self.config.trading.max_position_size)

    def update_position(self, position_id: str, position_data: Position):
        """Update position data."""
        self.current_positions[position_id] = position_data

    def remove_position(self, position_id: str):
        """Remove position from tracking."""
        if position_id in self.current_positions:
            del self.current_positions[position_id]

    def update_pnl(self, pnl: float):
        """Update daily P&L."""
        self.daily_pnl += pnl

    def create_position(
        self,
        position_id: str,
        token_address: str,
        entry_price: float,
        amount: float,
        side: str
    ) -> Position:
        """
        Create a new position with continuous-time calculus parameters.
        """
        if not size_allowed(amount, self.config.trading.sol):
            minimum, maximum = bounds(self.config.trading.sol)
            raise ValueError(f"SOL size {amount} outside {minimum}-{maximum}")

        position = Position(
            position_id=position_id,
            token_address=token_address,
            entry_price=entry_price,
            current_price=entry_price,
            entry_time=time.time(),
            amount=amount,
            side=side
        )

        self.current_positions[position_id] = position
        logger.info(f"Position created: {position_id} at {entry_price}")
        return position
