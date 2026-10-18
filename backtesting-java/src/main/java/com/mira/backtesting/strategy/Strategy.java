package com.mira.backtesting.strategy;

import com.mira.backtesting.data.OHLCV;

import java.util.List;

/**
 * Base interface for trading strategies
 */
public interface Strategy {
    String getName();

    BacktestResult runBacktest(List<OHLCV> data);
}
