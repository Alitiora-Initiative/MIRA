"""
Recursive Scaling Engine - Handles step-wise milestone targets and perpetual scaling.
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from dataclasses import dataclass


@dataclass
class Milestone:
    """Scaling milestone target."""
    target_sol: float
    current_sol: float
    progress: float


class RecursiveScaling:
    """Recursive scaling engine for capital growth tracking."""

    def __init__(self, config):
        self.config = config
        self.scaling_config = config.scaling
        self.current_sol = 0.0
        self.milestone_target = self.scaling_config.milestone_target_sol
        logger.info("Recursive Scaling Engine initialized")

    async def update_capital(self, sol_amount: float):
        """
        Update current SOL capital and check for milestone targets.

        Args:
            sol_amount: Current SOL amount
        """
        self.current_sol = sol_amount
        milestone = self._calculate_milestone()

        if milestone.progress >= 1.0:
            logger.info(f"Milestone target reached: {milestone.target_sol} SOL")
            await self._advance_milestone()

    def _calculate_milestone(self) -> Milestone:
        """
        Calculate current milestone progress.

        Returns:
            Milestone object with progress data
        """
        progress = self.current_sol / self.milestone_target

        return Milestone(
            target_sol=self.milestone_target,
            current_sol=self.current_sol,
            progress=progress
        )

    async def _advance_milestone(self):
        """Advance to next milestone target."""
        self.milestone_target += 10  # Increment by 10 SOL
        logger.info(f"Advanced to next milestone: {self.milestone_target} SOL")

    async def check_perpetual_scaling(self, usd_value: float) -> bool:
        """
        Check if account valuation threshold for perpetual scaling is reached.

        Args:
            usd_value: Account valuation in USD

        Returns:
            True if threshold reached, False otherwise
        """
        threshold = self.scaling_config.perpetual_scaling_threshold_usd

        if usd_value >= threshold:
            logger.info(f"Perpetual scaling threshold reached: ${usd_value:.2f}")
            return True

        return False

    async def get_scaling_status(self) -> Dict[str, Any]:
        """
        Get current scaling status.

        Returns:
            Dictionary with scaling status data
        """
        milestone = self._calculate_milestone()

        return {
            "current_sol": self.current_sol,
            "milestone_target": self.milestone_target,
            "milestone_progress": milestone.progress,
            "perpetual_threshold": self.scaling_config.perpetual_scaling_threshold_usd
        }
