#!/usr/bin/env python3
"""
AI Trading Agent - Main Entry Point
"""

import asyncio
import yaml
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from core.engine import TradingEngine
from core.config import Config


def load_config(config_path: str = "config/config.yaml") -> Config:
    """Load configuration from YAML file."""
    load_dotenv()
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    return Config(**config_data)


async def main():
    """Main entry point for the trading agent."""
    logger.info("Starting AI Trading Agent...")

    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    config = load_config(str(config_path))

    logger.info(f"Environment: {config.general.environment}")
    logger.info(f"Trading mode: {config.general.environment}")

    # Initialize trading engine
    engine = TradingEngine(config)

    try:
        # Start the engine
        await engine.start()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        await engine.stop()


if __name__ == "__main__":
    asyncio.run(main())
