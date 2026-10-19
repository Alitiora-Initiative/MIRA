#!/usr/bin/env python3
"""
MIRA paper trading entrypoint.

Loads config.paper.yaml when config.yaml is absent. Never reads a seed phrase.
"""

import asyncio
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from loguru import logger

from core.config import Config
from core.engine import TradingEngine


def resolve_config_path() -> Path:
    override = os.environ.get("MIRA_CONFIG")
    if override:
        return Path(override)
    root = Path(__file__).resolve().parent.parent / "config"
    local = root / "config.yaml"
    if local.exists():
        return local
    return root / "config.paper.yaml"


def load_config(config_path: Path) -> Config:
    load_dotenv()
    with config_path.open("r", encoding="utf-8") as handle:
        config_data = yaml.safe_load(handle) or {}
    return Config.from_dict(config_data)


async def main() -> None:
    logger.info("Starting MIRA paper trading...")
    config_path = resolve_config_path()
    if not config_path.exists():
        logger.error(f"Config not found: {config_path}")
        raise SystemExit(1)

    config = load_config(config_path)
    minimum = config.trading.sol.get("min_trade")
    maximum = config.trading.sol.get("max_trade")
    logger.info(f"Config: {config_path.name}")
    logger.info(f"Environment: {config.general.environment}")
    logger.info(f"Account mode: {config.account_mode.mode}")
    logger.info(f"SOL clip: {minimum} – {maximum}")

    engine = TradingEngine(config)
    try:
        await engine.start()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as exc:
        logger.error(f"Fatal error: {exc}")
        raise
    finally:
        await engine.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
