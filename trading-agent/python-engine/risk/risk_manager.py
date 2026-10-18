"""
Risk Manager - Continuous-time calculus based risk management.
"""

from typing import Dict, List, Any
from loguru import logger
from dataclasses import dataclass
import time

from core.config import Config


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
        self.current_positions: Dict[str, Position] = {}
        self.risk_config = config.risk_management
        logger.info("Risk Manager initialized")

    async def evaluate_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate trading signals against risk criteria."""
        approved_signals = []

        for signal in signals:
            try:
                # Check if signal passes risk criteria
                if await self._check_signal_risk(signal):
                    approved_signals.append(signal)
                else:
                    logger.info(f"Signal rejected by risk manager: {signal}")

            except Exception as e:
                logger.error(f"Error evaluating signal: {e}")

        return approved_signals

    async def _check_signal_risk(self, signal: Dict[str, Any]) -> bool:
        """Check if a signal meets risk criteria."""
        # Check daily loss limit
        if self.daily_pnl < -self.config.trading.max_daily_loss:
            logger.warning("Daily loss limit reached, rejecting signal")
            return False

        # Check max open positions
        if len(self.current_positions) >= self.config.trading.max_open_positions:
            logger.warning("Max open positions reached, rejecting signal")
            return False

        # Check position size
        if signal.get('amount', 0) > self.config.trading.max_position_size:
            logger.warning("Position size exceeds limit, rejecting signal")
            return False

        # Check confidence threshold
        confidence = signal.get('confidence', 0)
        min_confidence = 0.5
        if confidence < min_confidence:
            logger.warning(f"Signal confidence too low: {confidence}")
            return False

        return True

    async def evaluate_arbitrage(self, opportunity: Dict[str, Any]) -> bool:
        """Evaluate arbitrage opportunity against risk criteria."""
        # Check profit threshold
        min_profit = self.config.strategies.arbitrage.get('min_profit_percentage', 0.5) / 100
        if opportunity['profit_percentage'] < min_profit:
            return False

        # Check if we have sufficient balance
        # (Would check actual balances in production)

        return True

    async def check_portfolio_risk(self):
        """Check overall portfolio risk."""
        try:
            # Calculate portfolio metrics
            total_exposure = sum(pos.get('value', 0) for pos in self.current_positions.values())

            # Check diversification
            max_single_position = max(
                (pos.get('value', 0) for pos in self.current_positions.values()),
                default=0
            )

            if total_exposure > 0:
                concentration = max_single_position / total_exposure
                if concentration > self.config.risk_management.diversification_threshold:
                    logger.warning(f"Portfolio concentration too high: {concentration:.2%}")

            # Check drawdown
            # (Would calculate from historical data)

        except Exception as e:
            logger.error(f"Error checking portfolio risk: {e}")

    async def check_positions(self):
        """Check individual positions for risk using continuous-time calculus."""
        for position_id, position in self.current_positions.items():
            try:
                # Real-Time Price Tracking Matrix (Pt) against Initial Position Entry Cost Basis (P0)
                pt = position.current_price
                p0 = position.entry_price

                # Calculate price change percentage
                price_change_pct = (pt - p0) / p0

                # Check stop loss floor
                if price_change_pct <= self.risk_config.stop_loss_floor:
                    logger.info(f"Stop loss floor triggered for position {position_id}: {price_change_pct:.2%}")
                    return await self._close_position(position_id, "stop_loss_floor")

                # Check stop loss ceiling guardrail
                if price_change_pct <= self.risk_config.stop_loss_ceiling:
                    logger.info(f"Stop loss ceiling triggered for position {position_id}: {price_change_pct:.2%}")
                    return await self._close_position(position_id, "stop_loss_ceiling")

                # Check take profit floor
                if price_change_pct >= self.risk_config.take_profit_floor:
                    logger.info(f"Take profit floor triggered for position {position_id}: {price_change_pct:.2%}")
                    return await self._close_position(position_id, "take_profit_floor")

                # Check take profit cap
                if price_change_pct >= self.risk_config.take_profit_cap:
                    logger.info(f"Take profit cap triggered for position {position_id}: {price_change_pct:.2%}")
                    return await self._close_position(position_id, "take_profit_cap")

            except Exception as e:
                logger.error(f"Error checking position {position_id}: {e}")

    async def _close_position(self, position_id: str, reason: str) -> bool:
        """
        Close position and execute cross-swap back to native SOL.

        Args:
            position_id: Position identifier
            reason: Reason for closing position

        Returns:
            True if successful, False otherwise
        """
        try:
            position = self.current_positions.get(position_id)
            if not position:
                return False

            logger.info(f"Closing position {position_id} via cross-swap to SOL: {reason}")

            # Remove from tracking
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
        """Calculate optimal position size based on risk parameters."""
        method = self.config.risk_management.position_sizing_method

        if method == 'fixed':
            return portfolio_value * self.config.trading.max_position_size

        elif method == 'kelly_criterion':
            # Kelly criterion calculation
            win_rate = signal.get('win_rate', 0.5)
            avg_win = signal.get('avg_win', 0.05)
            avg_loss = signal.get('avg_loss', 0.03)

            kelly_pct = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_pct = max(0, min(kelly_pct, 0.25))  # Cap at 25%

            return portfolio_value * kelly_pct

        elif method == 'risk_parity':
            # Risk parity - equal risk contribution
            return portfolio_value / self.config.trading.max_open_positions

        return portfolio_value * self.config.trading.max_position_size

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

        Args:
            position_id: Position identifier
            token_address: Token mint address
            entry_price: Entry price (P0)
            amount: Position amount
            side: 'buy' or 'sell'

        Returns:
            Position object
        """
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
