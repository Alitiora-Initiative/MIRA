"""
Test Run: Alpaca Paper Trading
Demonstrates MIRA executing a paper trade via Alpaca API
"""
import asyncio
import sys
import os
from loguru import logger
from exchanges.alpaca import AlpacaClient
from ai.hermes.agents import HermesOrchestrator, AgentTask

async def test_alpaca_paper_trade():
    """Execute a paper trading test run with Alpaca"""
    
    logger.info("=" * 60)
    logger.info("MIRA PAPER TRADING TEST RUN - ALPACA")
    logger.info("=" * 60)
    
    # Initialize Alpaca client (paper trading mode)
    # You'll need to set ALPACA_API_KEY and ALPACA_API_SECRET environment variables
    alpaca = AlpacaClient(paper=True)
    
    # Check account status
    logger.info("\n📊 Checking Alpaca paper trading account...")
    account = alpaca.get_account()
    
    if "error" in account:
        logger.error(f"❌ Failed to connect to Alpaca: {account['error']}")
        logger.info("\nTo fix this:")
        logger.info("1. Create an Alpaca account at https://alpaca.markets")
        logger.info("2. Enable paper trading in your Alpaca dashboard")
        logger.info("3. Get your API keys from the API Keys section")
        logger.info("4. Set environment variables:")
        logger.info("   export ALPACA_API_KEY='your_api_key'")
        logger.info("   export ALPACA_API_SECRET='your_api_secret'")
        return
    
    logger.info(f"✅ Account connected")
    logger.info(f"   Cash: ${account.get('cash', 0):.2f}")
    logger.info(f"   Portfolio Value: ${account.get('portfolio_value', 0):.2f}")
    logger.info(f"   Buying Power: ${account.get('buying_power', 0):.2f}")
    
    # Initialize Hermes agents for decision making
    logger.info("\n🤖 Initializing Hermes AI Agents...")
    hermes_config = {
        "data_sources": ["twitter", "reddit", "news"],
        "target_languages": ["python"],
        "optimization_method": "bayesian",
        "max_position_size": 0.1
    }
    hermes = HermesOrchestrator(hermes_config)
    logger.info("✅ AI Agents initialized")
    
    # Run research agent to analyze a stock
    logger.info("\n🔍 Running Research Agent for AAPL...")
    research_task = AgentTask(
        task_id="research_001",
        task_type="research",
        payload={"symbol": "AAPL"}
    )
    research_result = await hermes.process_task(research_task)
    logger.info(f"✅ Research complete: {research_result}")
    
    # Run risk agent to assess trade
    logger.info("\n⚠️  Running Risk Agent...")
    risk_task = AgentTask(
        task_id="risk_001",
        task_type="risk",
        payload={
            "symbol": "AAPL",
            "size": 1,
            "price": 175.00
        }
    )
    risk_result = await hermes.process_task(risk_task)
    logger.info(f"✅ Risk assessment: {risk_result}")
    
    # Execute paper trade if approved
    if risk_result.get("approved", False):
        logger.info("\n💰 Executing Paper Trade...")
        
        # Place a buy order for 1 share of AAPL
        order_result = alpaca.place_order(
            symbol="AAPL",
            qty=1,
            side="buy",
            order_type="market"
        )
        
        if "error" in order_result:
            logger.error(f"❌ Order failed: {order_result['error']}")
        else:
            logger.info(f"✅ Order placed successfully!")
            logger.info(f"   Order ID: {order_result.get('order_id')}")
            logger.info(f"   Status: {order_result.get('status')}")
            
            # Check positions after trade
            logger.info("\n📈 Checking current positions...")
            positions = alpaca.get_positions()
            if positions:
                logger.info(f"   Open positions: {len(positions)}")
                for pos in positions:
                    logger.info(f"   - {pos['symbol']}: {pos['qty']} shares (${pos['market_value']:.2f})")
            else:
                logger.info("   No open positions")
    else:
        logger.info("\n⛔ Trade not approved by Risk Agent")
        logger.info(f"   Reason: {risk_result.get('recommendations', [])}")
    
    logger.info("\n" + "=" * 60)
    logger.info("PAPER TRADING TEST RUN COMPLETE")
    logger.info("=" * 60)

if __name__ == "__main__":
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    asyncio.run(test_alpaca_paper_trade())
