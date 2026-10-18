"""
Jupiter Aggregator V6 integration for optimal slippage mitigation and trade routing.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from loguru import logger
from dataclasses import dataclass


@dataclass
class QuoteRequest:
    """Quote request parameters."""
    input_mint: str
    output_mint: str
    amount: int
    slippage_bps: int = 100


@dataclass
class QuoteResponse:
    """Quote response data."""
    in_amount: int
    out_amount: int
    price_impact_pct: float
    route_plan: List[Dict]
    context_slot: int


class JupiterRouter:
    """Jupiter Aggregator V6 API client."""

    def __init__(self, config):
        self.config = config
        self.api_url = "https://quote-api.jup.ag/v6"
        logger.info("Jupiter Router initialized")

    async def get_quote(self, request: QuoteRequest) -> Optional[QuoteResponse]:
        """
        Get swap quote from Jupiter Aggregator.

        Args:
            request: QuoteRequest with input/output mints and amount

        Returns:
            QuoteResponse or None
        """
        try:
            url = f"{self.api_url}/quote"
            params = {
                "inputMint": request.input_mint,
                "outputMint": request.output_mint,
                "amount": request.amount,
                "slippageBps": request.slippage_bps,
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Jupiter quote error: {data['error']}")
                        return None

                    return QuoteResponse(
                        in_amount=int(data['inAmount']),
                        out_amount=int(data['outAmount']),
                        price_impact_pct=float(data.get('priceImpactPct', 0)),
                        route_plan=data.get('routePlan', []),
                        context_slot=int(data.get('contextSlot', 0))
                    )

        except Exception as e:
            logger.error(f"Error getting Jupiter quote: {e}")
            return None

    async def get_swap_transaction(
        self,
        quote_response: QuoteResponse,
        user_public_key: str,
        prioritization_fee_lamports: int = 0
    ) -> Optional[Dict]:
        """
        Get swap transaction from Jupiter.

        Args:
            quote_response: QuoteResponse from get_quote
            user_public_key: User's Solana public key
            prioritization_fee_lamports: Optional priority fee

        Returns:
            Transaction data or None
        """
        try:
            url = f"{self.api_url}/swap"
            payload = {
                "quoteResponse": {
                    "inAmount": str(quote_response.in_amount),
                    "outAmount": str(quote_response.out_amount),
                    "routePlan": quote_response.route_plan,
                    "contextSlot": quote_response.context_slot
                },
                "userPublicKey": user_public_key,
                "prioritizationFeeLamports": prioritization_fee_lamports,
                "wrapAndUnwrapSol": True
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    data = await response.json()

                    if data.get('error'):
                        logger.error(f"Jupiter swap error: {data['error']}")
                        return None

                    return data

        except Exception as e:
            logger.error(f"Error getting swap transaction: {e}")
            return None

    async def execute_swap(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        user_public_key: str,
        slippage_bps: int = 100,
        priority_fee_lamports: int = 0
    ) -> Optional[Dict]:
        """
        Execute a swap through Jupiter Aggregator.

        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount in smallest unit (lamports)
            user_public_key: User's Solana public key
            slippage_bps: Slippage tolerance in basis points (1 = 0.01%)
            priority_fee_lamports: Priority fee for transaction

        Returns:
            Transaction data or None
        """
        try:
            quote_request = QuoteRequest(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=amount,
                slippage_bps=slippage_bps
            )

            quote = await self.get_quote(quote_request)
            if not quote:
                return None

            logger.info(f"Quote received: {quote.in_amount} -> {quote.out_amount}")

            transaction = await self.get_swap_transaction(
                quote,
                user_public_key,
                priority_fee_lamports
            )

            if transaction:
                logger.info("Swap transaction generated successfully")
                return transaction

            return None

        except Exception as e:
            logger.error(f"Error executing swap: {e}")
            return None

    async def get_all_tokens(self) -> Optional[List[Dict]]:
        """
        Get list of all tokens supported by Jupiter.

        Returns:
            List of token data or None
        """
        try:
            url = f"{self.api_url}/tokens"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return data

        except Exception as e:
            logger.error(f"Error getting token list: {e}")
            return None

    async def get_indexed_routes(self) -> Optional[Dict]:
        """
        Get indexed route information.

        Returns:
            Route data or None
        """
        try:
            url = f"{self.api_url}/indexed-route-map"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return data

        except Exception as e:
            logger.error(f"Error getting indexed routes: {e}")
            return None
