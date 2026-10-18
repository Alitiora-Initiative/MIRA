"""
Claude API Integration for Strategy Development
"""
import anthropic
from loguru import logger
from typing import Dict, List, Optional
import os

class ClaudeStrategyEngine:
    """Claude-powered strategy development and analysis"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set - Claude integration disabled")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate_strategy(self, market_context: str, risk_tolerance: str) -> str:
        """Generate trading strategy using Claude"""
        if not self.client:
            return "Claude client not initialized"
        
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"""
                    Generate a trading strategy based on:
                    Market Context: {market_context}
                    Risk Tolerance: {risk_tolerance}
                    
                    Provide strategy in Python code with clear entry/exit rules.
                    """
                }]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"Error: {str(e)}"
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze market sentiment from text"""
        if not self.client:
            return {"error": "Claude client not initialized"}
        
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"""
                    Analyze the sentiment of this text about trading/crypto:
                    "{text}"
                    
                    Return JSON with keys: sentiment (bullish/bearish/neutral), confidence (0-1), factors (list)
                    """
                }]
            )
            return {"analysis": message.content[0].text}
        except Exception as e:
            logger.error(f"Claude sentiment analysis error: {e}")
            return {"error": str(e)}
