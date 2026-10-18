package com.mira.backtesting.data;

import java.util.ArrayList;
import java.util.List;

/**
 * Data Store for historical market data
 * Loads and caches OHLCV data
 */
public class DataStore {
    private final List<OHLCV> cache;

    public DataStore() {
        this.cache = new ArrayList<>();
    }

    /**
     * Load historical data for a symbol
     */
    public List<OHLCV> loadHistoricalData(String symbol, String timeframe, int limit) {
        // In production, this would load from database
        // For now, generate synthetic data
        return generateSyntheticData(symbol, limit);
    }

    /**
     * Generate synthetic OHLCV data for testing
     */
    private List<OHLCV> generateSyntheticData(String symbol, int count) {
        List<OHLCV> data = new ArrayList<>();
        double price = 100.0;

        for (int i = 0; i < count; i++) {
            double open = price;
            double close = price + (Math.random() - 0.5) * 2.0;
            double high = Math.max(open, close) + Math.random() * 0.5;
            double low = Math.min(open, close) - Math.random() * 0.5;
            double volume = 1000 + Math.random() * 5000;

            data.add(new OHLCV(
                System.currentTimeMillis() - (count - i) * 3600000L,
                open,
                high,
                low,
                close,
                volume
            ));

            price = close;
        }

        return data;
    }

    /**
     * Save data to cache
     */
    public void saveData(String symbol, List<OHLCV> data) {
        cache.addAll(data);
    }

    /**
     * Clear cache
     */
    public void clearCache() {
        cache.clear();
    }
}
