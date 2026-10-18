"""
Solana Exchange Manager - Handles Solana DEX operations via Jupiter and Helius.
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger

from core.config import Config
from solana.helius_client import HeliusClient
from solana.jupiter_router import JupiterRouter
from solana.jito_bundle import JitoBundle
from solana.mpc_signer import MPCSigner


class SolanaExchangeManager:
    """Manages Solana DEX operations."""

    def __init__(self, config: Config):
        self.config = config
        self.helius_client = HeliusClient(config)
        self.jupiter_router = JupiterRouter(config)
        self.jito_bundle = JitoBundle(config)
        self.mpc_signer = MPCSigner(config)
        logger.info("Solana Exchange Manager initialized")

    async def initialize(self):
        """Initialize Solana connections."""
        logger.info("Initializing Solana connections...")
        logger.info("Solana Exchange Manager ready")

    async def get_market_data(self, token_address: str) -> Optional[Dict[str, Any]]:
        """Get current market data for a token."""
        try:
            price_data = await self.helius_client.get_token_price(token_address)
            if price_data:
                return {
                    'price_usd': price_data.price_usd,
                    'price_change_24h': price_data.price_change_24h,
                    'volume_24h': price_data.volume_24h
                }
            return None
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None

    async def get_historical_data(self, token_address: str, timeframe: str = '1h', limit: int = 100) -> Optional[list]:
        """Get historical OHLCV data."""
        try:
            candles = await self.helius_client.get_ohlcv_candles(token_address, timeframe, limit)
            return candles
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return None

    async def execute_swap(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        user_public_key: str,
        biometric_token: str,
        slippage_bps: int = 100
    ) -> Optional[Dict[str, Any]]:
        """Execute swap via Jupiter with Jito MEV protection and MPC signing."""
        try:
            # Get swap transaction from Jupiter
            transaction = await self.jupiter_router.execute_swap(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=amount,
                user_public_key=user_public_key,
                slippage_bps=slippage_bps,
                priority_fee_lamports=self.config.solana.jito_tip_lamports
            )

            if not transaction:
                return None

            # Sign transaction via MPC
            transaction_bytes = bytes.fromhex(transaction['swapTransaction'])
            signed_transaction = await self.mpc_signer.sign_transaction(
                transaction_bytes,
                biometric_token
            )

            if not signed_transaction:
                return None

            # Send via Jito bundle
            tip_accounts = await self.jito_bundle.get_tip_accounts()
            if tip_accounts:
                bundle_id = await self.jito_bundle.send_transaction_with_tip(
                    signed_transaction,
                    tip_accounts[0],
                    self.config.solana.jito_tip_lamports
                )

                if bundle_id:
                    logger.info(f"Swap executed via Jito bundle: {bundle_id}")
                    return {'success': True, 'bundle_id': bundle_id}

            return {'success': False, 'error': 'Bundle send failed'}

        except Exception as e:
            logger.error(f"Error executing swap: {e}")
            return {'success': False, 'error': str(e)}

    async def get_balance(self, wallet_address: str) -> Optional[float]:
        """Get wallet SOL balance."""
        try:
            balance = await self.helius_client.get_wallet_balance(wallet_address)
            return balance
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None

    async def get_token_accounts(self, wallet_address: str) -> Optional[list]:
        """Get all token accounts for wallet."""
        try:
            accounts = await self.helius_client.get_token_accounts_by_owner(wallet_address)
            return accounts
        except Exception as e:
            logger.error(f"Error getting token accounts: {e}")
            return None

    async def shutdown(self):
        """Close connections."""
        logger.info("Closing Solana connections...")
        logger.info("Solana Exchange Manager shutdown complete")
