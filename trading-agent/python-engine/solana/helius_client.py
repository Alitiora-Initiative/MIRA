"""
Helius RPC client for Solana data aggregation.
Accesses real-time market charts, liquidity depth arrays, and OHLCV candlestick matrices.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from loguru import logger
from dataclasses import dataclass


@dataclass
class TokenPrice:
    """Token price data."""
    token_address: str
    price_usd: float
    price_change_24h: float
    volume_24h: float


@dataclass
class LiquidityDepth:
    """Liquidity depth data."""
    token_address: str
    asks: List[tuple]
    bids: List[tuple]
    total_liquidity_usd: float


@dataclass
class OHLCVCandle:
    """OHLCV candlestick data."""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class HeliusClient:
    """Helius RPC client for Solana data aggregation."""

    def __init__(self, config):
        self.config = config
        self.rpc_endpoint = config.solana.rpc_endpoint
        self.commitment = config.solana.commitment
        logger.info("Helius Client initialized")

    async def get_token_price(self, token_address: str) -> Optional[TokenPrice]:
        """
        Get current token price.

        Args:
            token_address: Solana token mint address

        Returns:
            TokenPrice object or None
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAssetPrice",
                "params": {
                    "id": token_address
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_endpoint, json=payload) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Helius price error: {data['error']}")
                        return None

                    result = data.get('result')
                    if not result:
                        return None

                    return TokenPrice(
                        token_address=token_address,
                        price_usd=float(result.get('price', 0)),
                        price_change_24h=float(result.get('change24h', 0)),
                        volume_24h=float(result.get('volume24h', 0))
                    )

        except Exception as e:
            logger.error(f"Error getting token price: {e}")
            return None

    async def get_liquidity_depth(self, token_address: str) -> Optional[LiquidityDepth]:
        """
        Get liquidity depth for a token.

        Args:
            token_address: Solana token mint address

        Returns:
            LiquidityDepth object or None
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getLiquidityDepth",
                "params": {
                    "id": token_address
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_endpoint, json=payload) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Helius liquidity error: {data['error']}")
                        return None

                    result = data.get('result')
                    if not result:
                        return None

                    return LiquidityDepth(
                        token_address=token_address,
                        asks=result.get('asks', []),
                        bids=result.get('bids', []),
                        total_liquidity_usd=float(result.get('totalLiquidity', 0))
                    )

        except Exception as e:
            logger.error(f"Error getting liquidity depth: {e}")
            return None

    async def get_ohlcv_candles(
        self,
        token_address: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> Optional[List[OHLCVCandle]]:
        """
        Get OHLCV candlestick data.

        Args:
            token_address: Solana token mint address
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch

        Returns:
            List of OHLCVCandle objects or None
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getOHLCV",
                "params": {
                    "id": token_address,
                    "timeframe": timeframe,
                    "limit": limit
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_endpoint, json=payload) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Helius OHLCV error: {data['error']}")
                        return None

                    result = data.get('result')
                    if not result:
                        return None

                    candles = []
                    for candle_data in result:
                        candles.append(OHLCVCandle(
                            timestamp=int(candle_data.get('timestamp', 0)),
                            open=float(candle_data.get('open', 0)),
                            high=float(candle_data.get('high', 0)),
                            low=float(candle_data.get('low', 0)),
                            close=float(candle_data.get('close', 0)),
                            volume=float(candle_data.get('volume', 0))
                        ))

                    return candles

        except Exception as e:
            logger.error(f"Error getting OHLCV candles: {e}")
            return None

    async def get_token_metadata(self, token_address: str) -> Optional[Dict[str, Any]]:
        """
        Get token metadata.

        Args:
            token_address: Solana token mint address

        Returns:
            Token metadata dictionary or None
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAsset",
                "params": {
                    "id": token_address
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_endpoint, json=payload) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Helius metadata error: {data['error']}")
                        return None

                    return data.get('result')

        except Exception as e:
            logger.error(f"Error getting token metadata: {e}")
            return None

    async def get_wallet_balance(self, wallet_address: str) -> Optional[float]:
        """
        Get wallet SOL balance.

        Args:
            wallet_address: Solana wallet address

        Returns:
            Balance in SOL or None
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet_address]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_endpoint, json=payload) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Helius balance error: {data['error']}")
                        return None

                    result = data.get('result')
                    if result:
                        return result['value'] / 1e9  # Convert lamports to SOL

                    return None

        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return None

    async def get_token_accounts_by_owner(
        self,
        wallet_address: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get all token accounts for a wallet.

        Args:
            wallet_address: Solana wallet address

        Returns:
            List of token account data or None
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet_address,
                    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.rpc_endpoint, json=payload) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Helius token accounts error: {data['error']}")
                        return None

                    return data.get('result', {}).get('value', [])

        except Exception as e:
            logger.error(f"Error getting token accounts: {e}")
            return None
