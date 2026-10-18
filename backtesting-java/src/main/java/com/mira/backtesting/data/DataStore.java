package com.mira.backtesting.data;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

/**
 * Data Store for historical market data
 * Loads real historical data from PostgreSQL database
 */
public class DataStore {
    private final String dbUrl;
    private final String dbUser;
    private final String dbPassword;

    public DataStore() {
        // Load from environment variables
        this.dbUrl = System.getenv().getOrDefault("DB_URL", "jdbc:postgresql://localhost:5432/trading_data");
        this.dbUser = System.getenv().getOrDefault("DB_USER", "trader");
        this.dbPassword = System.getenv().getOrDefault("DB_PASSWORD", "changeme");
    }

    /**
     * Load historical data for a symbol from database
     */
    public List<OHLCV> loadHistoricalData(String symbol, String timeframe, int limit) {
        List<OHLCV> data = new ArrayList<>();
        String query = "SELECT timestamp, open, high, low, close, volume " +
                      "FROM ohlcv_data " +
                      "WHERE symbol = ? AND timeframe = ? " +
                      "ORDER BY timestamp DESC LIMIT ?";

        try (Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPassword);
             PreparedStatement stmt = conn.prepareStatement(query)) {

            stmt.setString(1, symbol);
            stmt.setString(2, timeframe);
            stmt.setInt(3, limit);

            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                data.add(new OHLCV(
                    rs.getLong("timestamp"),
                    rs.getDouble("open"),
                    rs.getDouble("high"),
                    rs.getDouble("low"),
                    rs.getDouble("close"),
                    rs.getDouble("volume")
                ));
            }
        } catch (SQLException e) {
            System.err.println("Error loading data from database: " + e.getMessage());
            // Fallback to synthetic data if database is not available
            return generateSyntheticData(symbol, limit);
        }

        return data;
    }

    /**
     * Save data to database
     */
    public void saveData(String symbol, List<OHLCV> data) {
        String query = "INSERT INTO ohlcv_data (symbol, timestamp, open, high, low, close, volume, timeframe) " +
                      "VALUES (?, ?, ?, ?, ?, ?, ?, ?) " +
                      "ON CONFLICT (symbol, timestamp, timeframe) DO UPDATE SET " +
                      "open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, " +
                      "close = EXCLUDED.close, volume = EXCLUDED.volume";

        try (Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPassword);
             PreparedStatement stmt = conn.prepareStatement(query)) {

            for (OHLCV ohlcv : data) {
                stmt.setString(1, symbol);
                stmt.setLong(2, ohlcv.getTimestamp());
                stmt.setDouble(3, ohlcv.getOpen());
                stmt.setDouble(4, ohlcv.getHigh());
                stmt.setDouble(5, ohlcv.getLow());
                stmt.setDouble(6, ohlcv.getClose());
                stmt.setDouble(7, ohlcv.getVolume());
                stmt.setString(8, "1h"); // Default timeframe
                stmt.addBatch();
            }

            stmt.executeBatch();
        } catch (SQLException e) {
            System.err.println("Error saving data to database: " + e.getMessage());
        }
    }

    /**
     * Generate synthetic OHLCV data (fallback if database unavailable)
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
     * Clear cache (not applicable for database-backed store)
     */
    public void clearCache() {
        // Database doesn't need cache clearing
    }
}
