"""
Core Trading Engine - paper session by default.

This entrypoint does not submit live swaps, Jito bundles, or wallet signatures.
"""

import asyncio
import os
from loguru import logger

from core.config import Config
from risk.risk_manager import RiskManager
from database.db_manager import DatabaseManager
from account.account_manager import AccountManager
from paper.book import PaperBook
from paper.limits import bounds


class TradingEngine:
    """Main trading engine. Launch path is paper-only unless refused."""

    def __init__(self, config: Config):
        self.config = config
        self.running = False
        self.risk_manager = RiskManager(config)
        self.db_manager = DatabaseManager(config)
        self.account_manager = AccountManager(config)
        self.book = PaperBook(
            config.trading.sol,
            take_profit=abs(config.risk_management.take_profit_floor),
            stop_loss=abs(config.risk_management.stop_loss_floor),
        )
        logger.info("MIRA Trading Engine initialized")

    def paper_enabled(self) -> bool:
        mode = self.config.account_mode
        demo = mode.demo or {}
        return mode.mode == "demo" and bool(demo.get("paper_trading", False))

    async def start(self):
        """Start the paper trading engine."""
        if not self.paper_enabled():
            raise RuntimeError(
                "Refusing to start. Set account_mode.mode=demo and "
                "account_mode.demo.paper_trading=true. Live signing stays off."
            )

        minimum, maximum = bounds(self.config.trading.sol)
        logger.info(f"Paper session SOL clip {minimum} – {maximum}")
        logger.info("No live RPC, no Jito bundle, no seed phrase.")

        await self.db_manager.initialize()
        self.risk_manager.set_equity_basis(self.account_manager.demo_balance)

        cycles = int(os.environ.get("MIRA_PAPER_CYCLES", "0") or "0")
        pause = float(os.environ.get("MIRA_PAPER_SLEEP", "2") or "2")
        self.running = True
        step = 0
        try:
            while self.running:
                await self._paper_step(step)
                step += 1
                if cycles and step >= cycles:
                    logger.info(f"Paper session finished after {step} cycles")
                    break
                await asyncio.sleep(pause)
        finally:
            self.running = False

    async def _paper_step(self, step: int) -> None:
        action = self.book.decide(
            step,
            self.account_manager.current_balance,
            self.account_manager.positions,
            self.account_manager.entries,
        )
        if not action:
            if step % 5 == 0:
                logger.info(
                    f"PAPER scan {step} bank={self.account_manager.current_balance:.6f} SOL "
                    f"open={list(self.account_manager.positions) or 'none'}"
                )
            return

        result = self.account_manager.execute_trade(
            action["symbol"],
            action["side"],
            float(action["size_sol"]),
            float(action["price"]),
        )
        if not result.get("success"):
            logger.warning(f"Paper order rejected: {result.get('error')}")
            return

        trade = result["trade"]
        if action["side"] == "sell":
            ret = float(result.get("return_pct") or 0)
            self.risk_manager.update_pnl(float(action["size_sol"]) * ret)

        await self.db_manager.log_trade(
            {
                "token_address": action["symbol"],
                "input_mint": "SOL",
                "output_mint": action["symbol"],
                "amount": trade["size_sol"],
                "phi_score": action.get("phi"),
            },
            result,
        )
        logger.info(
            f"PAPER {action['side'].upper()} {trade['size_sol']} SOL {action['symbol']} "
            f"@ {action['price']:.6f} ({action['reason']}) "
            f"bank={result['balance']:.6f} SOL"
        )

    async def stop(self):
        """Stop the trading engine gracefully."""
        logger.info("Stopping MIRA paper engine...")
        self.running = False
        await self.db_manager.shutdown()
        fills = len(self.account_manager.trades)
        logger.info(
            f"MIRA paper engine stopped. fills={fills} "
            f"bank={self.account_manager.current_balance:.6f} SOL "
            f"pnl={self.account_manager.calculate_pnl():.6f} SOL"
        )
