"""
TradingView Webhook Receiver
Receives alerts from Pine Script indicators and forwards to trading engine.

The receiver does not trade by itself. It refuses every request unless
MIRA_WEBHOOK_KEY is set and presented in the X-Mira-Key header.
"""
import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from loguru import logger

from tradingview.auth import webhook_authorized

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


config = WebhookConfig()

_SIGNALS = {"BUY", "SELL", "MACRO_BULLISH", "MACRO_BEARISH", "VOLATILITY_SPIKE"}


@app.post("/api/v1/webhook/tradingview")
async def tradingview_webhook(
    alert: TradingViewAlert,
    x_mira_key: Optional[str] = Header(default=None),
):
    """Receive TradingView webhook alert. Unauthenticated callers are rejected."""
    expected = os.environ.get("MIRA_WEBHOOK_KEY", "")
    if not webhook_authorized(x_mira_key, expected):
        logger.warning("Rejected TradingView webhook: missing or invalid key")
        raise HTTPException(status_code=401, detail="unauthorized")

    logger.info(f"Received TradingView alert: {alert.signal_type} for {alert.symbol}")

    if alert.signal_type not in _SIGNALS:
        logger.warning(f"Unknown signal type: {alert.signal_type}")
        raise HTTPException(status_code=400, detail="Invalid signal type")

    if alert.price <= 0:
        raise HTTPException(status_code=400, detail="Invalid price")

    return {"status": "received", "alert_id": f"tv_{alert.timestamp}", "mode": "paper-queue"}


@app.get("/api/v1/tradingview/status")
async def tradingview_status():
    """Check TradingView integration status. Does not reveal whether a key is configured."""
    return {
        "status": "active" if config.enabled else "inactive",
        "webhook_url": "/api/v1/webhook/tradingview",
        "auth": "x-mira-key",
        "supported_signals": sorted(_SIGNALS),
    }


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("MIRA_WEBHOOK_HOST", "127.0.0.1")
    port = int(os.environ.get("MIRA_WEBHOOK_PORT", "8084"))
    uvicorn.run(app, host=host, port=port)
