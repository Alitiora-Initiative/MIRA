"""Guards for paper mode, SOL clip, and webhook auth."""

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from account.account_manager import AccountManager
from core.config import Config
from paper.book import PaperBook
from paper.limits import bounds, propose_size, size_allowed
from risk.risk_manager import RiskManager
from tradingview.auth import webhook_authorized

SOL = {"min_trade": 0.001, "max_trade": 10.0}


def paper_config(**overrides):
    data = {
        "general": {"environment": "paper"},
        "trading": {"max_position_size": 10, "sol": dict(SOL)},
        "account_mode": {
            "mode": "demo",
            "demo": {"paper_trading": True, "initial_balance_sol": 25},
        },
        "database": {"connection_string": "sqlite:///:memory:"},
    }
    data.update(overrides)
    return Config.from_dict(data)


def test_bounds_and_reject_outside_band():
    assert bounds(SOL) == (0.001, 10.0)
    assert size_allowed(0.001, SOL)
    assert size_allowed(10, SOL)
    assert not size_allowed(0.0009, SOL)
    assert not size_allowed(10.0001, SOL)
    assert not size_allowed(float("nan"), SOL)
    assert not size_allowed(-1, SOL)


def test_propose_size_stays_inside_band():
    dust = propose_size(25, 85, SOL)
    assert dust == 0.001
    full = propose_size(100, 99, SOL)
    assert full == 10
    assert propose_size(0.0005, 95, SOL) is None
    assert propose_size(25, 80, SOL) is None


def test_config_hydrates_nested_dataclasses():
    cfg = paper_config()
    assert cfg.general.environment == "paper"
    assert cfg.account_mode.mode == "demo"
    assert cfg.trading.sol["max_trade"] == 10.0
    assert cfg.solana.rpc_endpoint == ""


def test_paper_fills_and_live_refusal():
    account = AccountManager(paper_config())
    assert account.paper
    too_small = account.execute_trade("WIF", "buy", 0.0005, 0.01)
    too_big = account.execute_trade("WIF", "buy", 11, 0.01)
    assert not too_small["success"]
    assert not too_big["success"]

    opened = account.open_paper("WIF", 0.5, 0.01)
    assert opened["success"]
    assert account.current_balance == 24.5
    closed = account.close_paper("WIF", 0.011)
    assert closed["success"]
    assert account.current_balance > 24.5

    live = AccountManager(
        paper_config(account_mode={"mode": "live", "demo": {"paper_trading": False}, "live": {}})
    )
    refused = live.execute_trade("SOL", "buy", 0.01, 1)
    assert not refused["success"]
    assert "Live trading is disabled" in refused["error"]


def test_book_never_sizes_outside_band():
    account = AccountManager(paper_config())
    book = PaperBook(SOL, take_profit=0.10, stop_loss=0.10)
    for step in range(40):
        action = book.decide(step, account.current_balance, account.positions, account.entries)
        if not action:
            continue
        result = account.execute_trade(action["symbol"], action["side"], action["size_sol"], action["price"])
        assert result["success"], result
        if action["side"] == "buy":
            assert 0.001 <= action["size_sol"] <= 10
        assert account.current_balance >= -1e-9


def test_risk_manager_rejects_bad_sol_and_reads_positions():
    risk = RiskManager(paper_config())
    risk.set_equity_basis(25)

    async def run():
        assert not await risk._check_signal_risk({"amount": 12, "confidence": 0.9})
        assert not await risk._check_signal_risk({"amount": 0.0001, "confidence": 0.9})
        assert await risk._check_signal_risk({"amount": 0.2, "confidence": 0.8})
        try:
            risk.create_position("bad", "SOL", 1, 15, "buy")
            raise AssertionError("expected reject")
        except ValueError:
            pass
        risk.create_position("ok", "WIF", 1.5, 0.2, "buy")
        await risk.check_portfolio_risk()
        await risk.check_positions()

    asyncio.run(run())


def test_webhook_fails_closed():
    assert not webhook_authorized(None, "secret")
    assert not webhook_authorized("secret", "")
    assert not webhook_authorized("nope", "secret")
    assert webhook_authorized("secret", "secret")


if __name__ == "__main__":
    test_bounds_and_reject_outside_band()
    test_propose_size_stays_inside_band()
    test_config_hydrates_nested_dataclasses()
    test_paper_fills_and_live_refusal()
    test_book_never_sizes_outside_band()
    test_risk_manager_rejects_bad_sol_and_reads_positions()
    test_webhook_fails_closed()
    print("paper guard tests passed")
