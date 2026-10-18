package com.mira.backtesting.strategy;

import com.mira.backtesting.data.OHLCV;

import java.util.ArrayList;
import java.util.List;

/**
 * Φ Matrix filtering strategy
 * Simulates the Φ Matrix asset rating system in backtesting
 */
public class PhiMatrixStrategy implements Strategy {
    private static final double MIN_PHI_SCORE = 85.0;

    @Override
    public String getName() {
        return "phi_matrix_filter";
    }

    @Override
    public BacktestResult runBacktest(List<OHLCV> data) {
        BacktestResult result = new BacktestResult();

        if (data == null || data.isEmpty()) {
            return result;
        }

        int totalTrades = 0;
        int winningTrades = 0;
        int losingTrades = 0;
        double totalReturn = 0.0;
        double maxDrawdown = 0.0;
        double peakEquity = 0.0;
        double currentEquity = 10000.0; // Starting capital

        List<Double> returns = new ArrayList<>();

        // Simulate Φ Matrix filtering
        for (int i = 10; i < data.size(); i++) {
            OHLCV current = data.get(i);
            OHLCV previous = data.get(i - 1);

            // Calculate synthetic Φ score
            double phiScore = calculatePhiScore(data.subList(i - 10, i));

            // Only trade if Φ score meets threshold
            if (phiScore >= MIN_PHI_SCORE) {
                // Simulate trade
                double priceChange = (current.getClose() - previous.getClose()) / previous.getClose();
                double tradeReturn = priceChange * 0.5; // 50% position size

                currentEquity *= (1 + tradeReturn);
                returns.add(tradeReturn);

                totalTrades++;
                if (tradeReturn > 0) {
                    winningTrades++;
                } else {
                    losingTrades++;
                }

                // Track drawdown
                if (currentEquity > peakEquity) {
                    peakEquity = currentEquity;
                }
                double drawdown = (peakEquity - currentEquity) / peakEquity;
                if (drawdown > maxDrawdown) {
                    maxDrawdown = drawdown;
                }
            }
        }

        // Calculate metrics
        totalReturn = (currentEquity - 10000.0) / 10000.0;
        double winRate = totalTrades > 0 ? (double) winningTrades / totalTrades : 0.0;

        // Calculate Sharpe ratio (simplified)
        double sharpeRatio = 0.0;
        if (!returns.isEmpty()) {
            double meanReturn = returns.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            double stdReturn = Math.sqrt(returns.stream()
                .mapToDouble(r -> Math.pow(r - meanReturn, 2))
                .average()
                .orElse(0.0));
            sharpeRatio = stdReturn > 0 ? meanReturn / stdReturn * Math.sqrt(252) : 0.0;
        }

        // Calculate profit factor
        double profitFactor = 0.0;
        if (losingTrades > 0) {
            double avgWin = winningTrades > 0 ? 0.05 : 0.0; // Simplified
            double avgLoss = 0.03; // Simplified
            profitFactor = (avgWin * winningTrades) / (avgLoss * losingTrades);
        }

        result.setTotalTrades(totalTrades);
        result.setWinningTrades(winningTrades);
        result.setLosingTrades(losingTrades);
        result.setWinRate(winRate);
        result.setTotalReturn(totalReturn);
        result.setMaxDrawdown(maxDrawdown);
        result.setSharpeRatio(sharpeRatio);
        result.setProfitFactor(profitFactor);

        return result;
    }

    /**
     * Calculate synthetic Φ score for backtesting
     */
    private double calculatePhiScore(List<OHLCV> window) {
        // Simplified Φ score calculation
        // In production, this would use actual on-chain metrics

        double liquidityDensity = 0.8; // Simplified
        double holderConcentration = 0.3; // Simplified
        double volumetricVelocity = 0.5; // Simplified

        // Φ = ω1·Ld + ω2·(1-H) + ω3·Vv
        double phi = 0.5 * liquidityDensity + 0.3 * (1 - holderConcentration) + 0.2 * volumetricVelocity;
        return phi * 100;
    }
}
