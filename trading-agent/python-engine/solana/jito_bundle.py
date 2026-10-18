"""
Jito Block Engine integration for MEV protection via transaction bundles.
Bypasses public mempool front-running with priority validator tips.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from loguru import logger
from dataclasses import dataclass
import base64


@dataclass
class BundleTransaction:
    """Transaction to include in Jito bundle."""
    transaction: bytes
    description: str = ""


class JitoBundle:
    """Jito Block Engine client for MEV-protected transaction bundles."""

    def __init__(self, config):
        self.config = config
        self.endpoint = config.solana.jito_endpoint
        self.tip_lamports = config.solana.jito_tip_lamports
        logger.info("Jito Bundle Engine initialized")

    async def send_bundle(
        self,
        transactions: List[BundleTransaction],
        tip_lamports: Optional[int] = None
    ) -> Optional[str]:
        """
        Send transaction bundle to Jito Block Engine.

        Args:
            transactions: List of BundleTransaction objects
            tip_lamports: Optional override for tip amount

        Returns:
            Bundle ID or None
        """
        try:
            tip = tip_lamports or self.tip_lamports

            bundle_data = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "sendBundle",
                "params": [
                    [
                        base64.b64encode(tx.transaction).decode('utf-8')
                        for tx in transactions
                    ],
                    {
                        "tip": tip
                    }
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, json=bundle_data) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Jito bundle error: {data['error']}")
                        return None

                    bundle_id = data.get('result')
                    logger.info(f"Bundle sent successfully: {bundle_id}")
                    return bundle_id

        except Exception as e:
            logger.error(f"Error sending Jito bundle: {e}")
            return None

    async def get_bundle_status(self, bundle_id: str) -> Optional[Dict]:
        """
        Get status of a sent bundle.

        Args:
            bundle_id: Bundle ID from send_bundle

        Returns:
            Bundle status data or None
        """
        try:
            bundle_data = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "getBundleStatuses",
                "params": [[bundle_id]]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, json=bundle_data) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Jito status error: {data['error']}")
                        return None

                    return data.get('value')

        except Exception as e:
            logger.error(f"Error getting bundle status: {e}")
            return None

    async def create_tip_transaction(
        self,
        tip_account: str,
        tip_lamports: int
    ) -> Optional[bytes]:
        """
        Create tip transaction for Jito validator.

        Args:
            tip_account: Jito tip account address
            tip_lamports: Tip amount in lamports

        Returns:
            Transaction bytes or None
        """
        try:
            logger.info(f"Tip transaction to be created: {tip_lamports} lamports to {tip_account}")
            return None

        except Exception as e:
            logger.error(f"Error creating tip transaction: {e}")
            return None

    async def send_transaction_with_tip(
        self,
        transaction: bytes,
        tip_account: str,
        tip_lamports: Optional[int] = None
    ) -> Optional[str]:
        """
        Send a single transaction with Jito tip for priority execution.

        Args:
            transaction: Transaction bytes
            tip_account: Jito tip account address
            tip_lamports: Optional tip amount

        Returns:
            Bundle ID or None
        """
        try:
            tip = tip_lamports or self.tip_lamports
            tip_tx = await self.create_tip_transaction(tip_account, tip)

            if not tip_tx:
                return None

            bundle = [
                BundleTransaction(transaction=tip_tx, description="tip"),
                BundleTransaction(transaction=transaction, description="main")
            ]

            return await self.send_bundle(bundle)

        except Exception as e:
            logger.error(f"Error sending transaction with tip: {e}")
            return None

    async def get_tip_accounts(self) -> Optional[List[str]]:
        """
        Get list of Jito tip accounts.

        Returns:
            List of tip account addresses or None
        """
        try:
            url = "https://mainnet.block-engine.jito.wtf/api/v1/tip_accounts"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return data

        except Exception as e:
            logger.error(f"Error getting tip accounts: {e}")
            return None


