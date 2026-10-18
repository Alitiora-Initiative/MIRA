"""
Alpaca API Integration
Stock trading with paper trading support
"""
import alpaca_trade_api as trade
from alpaca_trade_api.stream import Stream
from loguru import logger
from typing import Dict, Optional
import os

class AlpacaClient:
    """Alpaca API client for stock trading"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, paper: bool = True):
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.api_secret = api_secret or os.getenv("ALPACA_API_SECRET")
        self.paper = paper
        
        if not self.api_key or not self.api_secret:
            logger.warning("Alpaca API credentials not set - integration disabled")
            self.api = None
        else:
            base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
            self.api = trade.REST(
                self.api_key,
                self.api_secret,
                base_url=base_url,
                api_version='v2'
            )
            logger.info(f"Alpaca client initialized (paper={paper})")
    
    def get_account(self) -> Dict:
        """Get account information"""
        if not self.api:
            return {"error": "Alpaca client not initialized"}
        try:
            account = self.api.get_account()
            return {
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "buying_power": float(account.buying_power)
            }
        except Exception as e:
            logger.error(f"Alpaca get_account error: {e}")
            return {"error": str(e)}
    
    def place_order(self, symbol: str, qty: int, side: str, order_type: str = "market") -> Dict:
        """Place an order"""
        if not self.api:
            return {"error": "Alpaca client not initialized"}
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force='day'
            )
            logger.info(f"Alpaca order placed: {side} {qty} {symbol}")
            return {"order_id": order.id, "status": order.status}
        except Exception as e:
            logger.error(f"Alpaca place_order error: {e}")
            return {"error": str(e)}
    
    def get_positions(self) -> list:
        """Get current positions"""
        if not self.api:
            return []
        try:
            positions = self.api.list_positions()
            return [
                {
                    "symbol": pos.symbol,
                    "qty": float(pos.qty),
                    "side": pos.side,
                    "market_value": float(pos.market_value)
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Alpaca get_positions error: {e}")
            return []
