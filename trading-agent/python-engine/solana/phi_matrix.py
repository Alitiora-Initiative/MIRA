"""
Φ Matrix Asset Rating System for Solana tokens.
Evaluates token contracts via objective on-chain mechanics.
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from dataclasses import dataclass
import aiohttp


@dataclass
class TokenMetrics:
    """Token on-chain metrics."""
    pool_tvl_usd: float
    mint_authority_revoked: bool
    burned_lp_tokens_percentage: float
    holder_distribution: Dict[str, int]
    volume_15m: float
    volume_24h_avg: float


class PhiMatrix:
    """Unified Asset Rating System (Φ Matrix)."""

    def __init__(self, config):
        self.config = config
        self.phi_config = config.phi_matrix
        self.rpc_endpoint = config.solana.rpc_endpoint
        logger.info("Φ Matrix initialized")

    async def calculate_phi_score(self, token_address: str) -> Optional[float]:
        """
        Calculate Φ score for a token.

        Formula: Φ = ω1 · Ld + ω2 · (1 - H) + ω3 · Vv

        Args:
            token_address: Solana token mint address

        Returns:
            Φ score (0-100) or None if gatekeeping fails
        """
        try:
            metrics = await self._fetch_token_metrics(token_address)
            if not metrics:
                return None

            # Gatekeeping check
            if not self._gatekeeping_check(metrics):
                logger.warning(f"Token {token_address} failed gatekeeping check")
                return None

            # Calculate components
            ld = self._calculate_liquidity_density(metrics.pool_tvl_usd)
            h = self._calculate_holder_concentration_skew(metrics.holder_distribution)
            vv = self._calculate_volumetric_velocity(metrics.volume_15m, metrics.volume_24h_avg)

            # Calculate Φ score
            phi = (
                self.phi_config.liquidity_density_weight * ld +
                self.phi_config.holder_concentration_weight * (1 - h) +
                self.phi_config.volumetric_velocity_weight * vv
            ) * 100

            logger.info(f"Φ score for {token_address}: {phi:.2f}%")
            return phi

        except Exception as e:
            logger.error(f"Error calculating Φ score: {e}")
            return None

    def _gatekeeping_check(self, metrics: TokenMetrics) -> bool:
        """
        Mandatory gatekeeping gateways.

        Returns:
            True if token passes gatekeeping, False otherwise
        """
        if not metrics.mint_authority_revoked:
            logger.warning("Mint authority not revoked")
            return False

        if metrics.burned_lp_tokens_percentage < 100:
            logger.warning(f"LP tokens not fully burned: {metrics.burned_lp_tokens_percentage}%")
            return False

        return True

    def _calculate_liquidity_density(self, pool_tvl_usd: float) -> float:
        """
        Calculate Liquidity Density (Ld).

        Ld = min(1.0, Pool_TVL / $10,000 USD Baseline)
        """
        baseline = self.phi_config.tvl_baseline_usd
        ld = min(1.0, pool_tvl_usd / baseline)
        return ld

    def _calculate_holder_concentration_skew(self, holder_distribution: Dict[str, int]) -> float:
        """
        Calculate Holder Concentration Skew (H).

        Normalized Herfindahl-Hirschman Index across top 10 token supply tracking vectors.
        """
        if not holder_distribution:
            return 1.0

        # Calculate HHI
        total_supply = sum(holder_distribution.values())
        if total_supply == 0:
            return 1.0

        hhi = sum((share / total_supply) ** 2 for share in holder_distribution.values())

        # Normalize to 0-1 range
        h = hhi

        return h

    def _calculate_volumetric_velocity(self, volume_15m: float, volume_24h_avg: float) -> float:
        """
        Calculate Volumetric Velocity Vector (Vv).

        Vv = tanh(ΔVolume_15m / Average_Volume_24h)
        """
        if volume_24h_avg == 0:
            return 0.0

        import math
        ratio = volume_15m / volume_24h_avg
        vv = math.tanh(ratio)
        return vv

    async def _fetch_token_metrics(self, token_address: str) -> Optional[TokenMetrics]:
        """
        Fetch token on-chain metrics via Helius RPC and DexScreener API.

        Args:
            token_address: Solana token mint address

        Returns:
            TokenMetrics object or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Fetch pool data from DexScreener
                pool_data = await self._fetch_dexscreener_data(session, token_address)
                if not pool_data:
                    return None

                # Fetch holder distribution from Helius
                holder_data = await self._fetch_holder_distribution(session, token_address)

                return TokenMetrics(
                    pool_tvl_usd=pool_data.get('liquidity', {}).get('usd', 0),
                    mint_authority_revoked=pool_data.get('mintAuthorityRevoked', False),
                    burned_lp_tokens_percentage=pool_data.get('burnedLpPercentage', 0),
                    holder_distribution=holder_data,
                    volume_15m=pool_data.get('volume', {}).get('h15', 0),
                    volume_24h_avg=pool_data.get('volume', {}).get('h24', 0) / 96
                )

        except Exception as e:
            logger.error(f"Error fetching token metrics: {e}")
            return None

    async def _fetch_dexscreener_data(self, session: aiohttp.ClientSession, token_address: str) -> Optional[Dict]:
        """Fetch token data from DexScreener API."""
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            async with session.get(url) as response:
                data = await response.json()
                if data.get('pairs'):
                    return data['pairs'][0]
                return None
        except Exception as e:
            logger.error(f"Error fetching DexScreener data: {e}")
            return None

    async def _fetch_holder_distribution(self, session: aiohttp.ClientSession, token_address: str) -> Dict[str, int]:
        """Fetch holder distribution from Helius RPC."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenLargestAccounts",
                "params": [token_address, 10]
            }

            async with session.post(self.rpc_endpoint, json=payload) as response:
                data = await response.json()
                if data.get('result'):
                    holders = {}
                    for account in data['result']['value']:
                        holders[account['address']] = int(account['amount'])
                    return holders
                return {}
        except Exception as e:
            logger.error(f"Error fetching holder distribution: {e}")
            return {}

    async def evaluate_token(self, token_address: str) -> Dict[str, Any]:
        """
        Evaluate a token for trading eligibility.

        Args:
            token_address: Solana token mint address

        Returns:
            Evaluation result with Φ score and pass/fail status
        """
        phi_score = await self.calculate_phi_score(token_address)

        result = {
            'token_address': token_address,
            'phi_score': phi_score,
            'passed': phi_score is not None and phi_score >= self.phi_config.minimum_phi_score,
            'minimum_required': self.phi_config.minimum_phi_score
        }

        logger.info(f"Token evaluation: {result}")
        return result
