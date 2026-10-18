"""
Binance API Integration
Crypto spot and futures trading
"""
from binance.client import Client
from binance.enums import *
from loguru import logger
from typing import Dict, Optional
import os

class BinanceClient:
    """Binance API client for crypto trading"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: bool = False):
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        self.testnet = testnet
        
        if not self.api_key or not self.api_secret:
            logger.warning("Binance API credentials not set - integration disabled")
            self.client = None
        else:
            self.client = Client(self.api_key, self.api_secret, testnet=testnet)
            logger.info(f"Binance client initialized (testnet={testnet})")
    
    def get_account(self) -> Dict:
        """Get account information"""
        if not self.client:
            return {"error": "Binance client not initialized"}
        try:
            account = self.client.get_account()
            balances = {b['asset']: float(b['free']) for b in account['balances'] if float(b['free']) > 0}
            return {"balances": balances}
        except Exception as e:
            logger.error(f"Binance get_account error: {e}")
            return {"error": str(e)}
    
    def place_order(self, symbol: str, quantity: float, side: str, order_type: str = "MARKET") -> Dict:
        """Place an order"""
        if not self.client:
            return {"error": "Binance client not initialized"}
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=quantity
            )
            logger.info(f"Binance order placed: {side} {quantity} {symbol}")
            return {"order_id": order['orderId'], "status": order['status']}
        except Exception as e:
            logger.error(f"Binance place_order error: {e}")
            return {"error": str(e)}
    
    def get_ticker_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        if not self.client:
            return 0.0
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Binance get_ticker_price error: {e}")
            return 0.0
