"""
TradingView Webhook Receiver
Receives alerts from Pine Script indicators and forwards to trading engine
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger
from typing import Optional
import httpx

app = FastAPI(title="MIRA TradingView Webhook")

class TradingViewAlert(BaseModel):
    symbol: str
    signal_type: str  # BUY, SELL, MACRO_BULLISH, MACRO_BEARISH, VOLATILITY_SPIKE
    price: float
    timestamp: int
    strategy: Optional[str] = None
    confidence: Optional[float] = None

class WebhookConfig:
    def __init__(self):
        self.enabled = True
        self.allowed_sources = ["tradingview"]
        self.api_keys = {}

config = WebhookConfig()

@app.post("/api/v1/webhook/tradingview")
async def tradingview_webhook(alert: TradingViewAlert):
    """Receive TradingView webhook alert"""
    logger.info(f"Received TradingView alert: {alert.signal_type} for {alert.symbol} @ {alert.price}")
    
    # Validate alert
    if alert.signal_type not in ["BUY", "SELL", "MACRO_BULLISH", "MACRO_BEARISH", "VOLATILITY_SPIKE"]:
        logger.warning(f"Unknown signal type: {alert.signal_type}")
        raise HTTPException(status_code=400, detail="Invalid signal type")
    
    # Forward to Python core engine
    # In production, this would call the trading engine directly
    await forward_to_core(alert)
    
    return {"status": "received", "alert_id": f"tv_{alert.timestamp}"}

async def forward_to_core(alert: TradingViewAlert):
    """Forward alert to core trading engine"""
    logger.info(f"Forwarding alert to core engine: {alert.signal_type}")
    # In production, this would make an HTTP call to the Python engine
    # or use gRPC to communicate with the core orchestrator

@app.get("/api/v1/tradingview/status")
async def tradingview_status():
    """Check TradingView integration status"""
    return {
        "status": "active" if config.enabled else "inactive",
        "webhook_url": "/api/v1/webhook/tradingview",
        "supported_signals": ["BUY", "SELL", "MACRO_BULLISH", "MACRO_BEARISH", "VOLATILITY_SPIKE"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)
