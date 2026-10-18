"""
Trigger.trade Integration
Route TradingView alerts to Telegram and brokers
"""
import httpx
from loguru import logger
from typing import Dict, Optional
import os

class TriggerTradeClient:
    """Trigger.trade client for webhook routing"""
    
    def __init__(self, webhook_url: Optional[str] = None, telegram_token: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("TRIGGER_WEBHOOK_URL")
        self.telegram_token = telegram_token or os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not self.webhook_url:
            logger.warning("Trigger.trade webhook URL not set - integration disabled")
    
    async def send_alert(self, alert: Dict) -> Dict:
        """Send alert to Trigger.trade"""
        if not self.webhook_url:
            return {"error": "Trigger.trade webhook URL not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=alert, timeout=10.0)
                response.raise_for_status()
                logger.info(f"Alert sent to Trigger.trade: {alert.get('signal_type')}")
                return {"status": "sent", "response": response.json()}
        except Exception as e:
            logger.error(f"Trigger.trade send_alert error: {e}")
            return {"error": str(e)}
    
    async def send_telegram_notification(self, chat_id: str, message: str) -> Dict:
        """Send notification via Telegram"""
        if not self.telegram_token:
            return {"error": "Telegram bot token not configured"}
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={
                    "chat_id": chat_id,
                    "text": message
                })
                response.raise_for_status()
                logger.info(f"Telegram notification sent to {chat_id}")
                return {"status": "sent"}
        except Exception as e:
            logger.error(f"Telegram notification error: {e}")
            return {"error": str(e)}
