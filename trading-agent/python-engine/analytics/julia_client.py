"""
HTTP client for Julia analytics services
Interfaces with portfolio optimizer and risk simulation engines
"""

import aiohttp
from typing import Dict, Any, List, Optional
from loguru import logger


class JuliaAnalyticsClient:
    """HTTP client for Julia analytics services."""

    def __init__(self, portfolio_endpoint: str = None, risk_endpoint: str = None):
        """
        Initialize Julia analytics client.

        Args:
            portfolio_endpoint: Portfolio optimizer URL (default: http://localhost:8081)
            risk_endpoint: Risk simulation URL (default: http://localhost:8082)
        """
        self.portfolio_endpoint = portfolio_endpoint or "http://localhost:8081"
        self.risk_endpoint = risk_endpoint or "http://localhost:8082"

    async def optimize_portfolio(
        self,
        assets: List[str],
        expected_returns: List[float],
        covariance_matrix: List[List[float]],
        max_positions: int = 20,
        max_position_weight: float = 0.2,
        min_return: float = 0.0
    ) -> Optional[Dict[str, Any]]:
        """
        Optimize portfolio using mean-variance optimization.

        Args:
            assets: List of asset symbols
            expected_returns: Expected returns for each asset
            covariance_matrix: Covariance matrix of returns
            max_positions: Maximum number of positions
            max_position_weight: Maximum weight per position
            min_return: Minimum expected return

        Returns:
            Optimization result or None
        """
        try:
            payload = {
                "assets": assets,
                "expected_returns": expected_returns,
                "covariance_matrix": covariance_matrix,
                "max_positions": max_positions,
                "max_position_weight": max_position_weight,
                "min_return": min_return
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.portfolio_endpoint}/optimize",
                    json=payload
                ) as response:
                    data = await response.json()
                    return data
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            return None

    async def optimize_cvar(
        self,
        assets: List[str],
        expected_returns: List[float],
        covariance_matrix: List[List[float]],
        max_positions: int = 20,
        max_position_weight: float = 0.2
    ) -> Optional[Dict[str, Any]]:
        """
        Optimize portfolio using CVaR (Conditional Value at Risk).

        Args:
            assets: List of asset symbols
            expected_returns: Expected returns for each asset
            covariance_matrix: Covariance matrix of returns
            max_positions: Maximum number of positions
            max_position_weight: Maximum weight per position

        Returns:
            CVaR optimization result or None
        """
        try:
            payload = {
                "assets": assets,
                "expected_returns": expected_returns,
                "covariance_matrix": covariance_matrix,
                "max_positions": max_positions,
                "max_position_weight": max_position_weight
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.portfolio_endpoint}/optimize/cvar",
                    json=payload
                ) as response:
                    data = await response.json()
                    return data
        except Exception as e:
            logger.error(f"Error optimizing CVaR: {e}")
            return None

    async def monte_carlo_var(
        self,
        portfolio_value: float,
        assets: List[str],
        weights: List[float],
        returns: List[List[float]],
        confidence_level: float = 0.95,
        time_horizon_days: int = 30,
        num_simulations: int = 10000
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate VaR using Monte Carlo simulation.

        Args:
            portfolio_value: Current portfolio value
            assets: List of asset symbols
            weights: Current portfolio weights
            returns: Historical returns for each asset
            confidence_level: Confidence level for VaR
            time_horizon_days: Time horizon in days
            num_simulations: Number of Monte Carlo simulations

        Returns:
            VaR result or None
        """
        try:
            payload = {
                "portfolio_value": portfolio_value,
                "assets": assets,
                "weights": weights,
                "returns": returns,
                "confidence_level": confidence_level,
                "time_horizon_days": time_horizon_days,
                "num_simulations": num_simulations
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.risk_endpoint}/risk/var",
                    json=payload
                ) as response:
                    data = await response.json()
                    return data
        except Exception as e:
            logger.error(f"Error calculating Monte Carlo VaR: {e}")
            return None

    async def gbm_simulation(
        self,
        portfolio_value: float,
        assets: List[str],
        weights: List[float],
        returns: List[List[float]],
        confidence_level: float = 0.95,
        time_horizon_days: int = 30,
        num_simulations: int = 10000
    ) -> Optional[Dict[str, Any]]:
        """
        Simulate portfolio using Geometric Brownian Motion.

        Args:
            portfolio_value: Current portfolio value
            assets: List of asset symbols
            weights: Current portfolio weights
            returns: Historical returns for each asset
            confidence_level: Confidence level for VaR
            time_horizon_days: Time horizon in days
            num_simulations: Number of simulations

        Returns:
            GBM simulation result or None
        """
        try:
            payload = {
                "portfolio_value": portfolio_value,
                "assets": assets,
                "weights": weights,
                "returns": returns,
                "confidence_level": confidence_level,
                "time_horizon_days": time_horizon_days,
                "num_simulations": num_simulations
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.risk_endpoint}/risk/gbm",
                    json=payload
                ) as response:
                    data = await response.json()
                    return data
        except Exception as e:
            logger.error(f"Error running GBM simulation: {e}")
            return None
