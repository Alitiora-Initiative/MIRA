package com.mira.backtesting;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.mira.backtesting.data.DataStore;
import com.mira.backtesting.strategy.Strategy;
import com.mira.backtesting.strategy.PhiMatrixStrategy;
import spark.Spark;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Main Backtesting Engine
 * Orchestrates backtesting operations and provides HTTP API
 */
public class BacktestingEngine {
    private final DataStore dataStore;
    private final Map<String, Strategy> strategies;
    private final Gson gson;

    public BacktestingEngine() {
        this.dataStore = new DataStore();
        this.strategies = new ConcurrentHashMap<>();
        this.gson = new Gson();

        // Register built-in strategies
        registerStrategy(new PhiMatrixStrategy());
    }

    public void registerStrategy(Strategy strategy) {
        strategies.put(strategy.getName(), strategy);
        System.out.println("Registered strategy: " + strategy.getName());
    }

    public void start(int port) {
        System.out.println("Starting MIRA Backtesting Engine on port " + port);
        Spark.port(port);

        // API Routes
        Spark.post("/api/v1/backtest/run", this::runBacktest);
        Spark.get("/api/v1/strategies", this::listStrategies);
        Spark.get("/api/v1/health", (req, res) -> {
            res.type("application/json");
            return gson.toJson(Map.of("status", "healthy"));
        });

        System.out.println("Backtesting Engine started successfully");
    }

    private String runBacktest(spark.Request req, spark.Response res) {
        try {
            JsonObject body = gson.fromJson(req.body(), JsonObject.class);

            String strategyName = body.get("strategy").getAsString();
            String symbol = body.get("symbol").getAsString();
            String timeframe = body.has("timeframe") ? body.get("timeframe").getAsString() : "1h";
            int limit = body.has("limit") ? body.get("limit").getAsInt() : 100;

            Strategy strategy = strategies.get(strategyName);
            if (strategy == null) {
                res.status(400);
                return gson.toJson(Map.of(
                    "success", false,
                    "error", "Strategy not found: " + strategyName
                ));
            }

            // Load data
            var data = dataStore.loadHistoricalData(symbol, timeframe, limit);
            if (data == null || data.isEmpty()) {
                res.status(400);
                return gson.toJson(Map.of(
                    "success", false,
                    "error", "No data available for symbol: " + symbol
                ));
            }

            // Run backtest
            var result = strategy.runBacktest(data);

            res.type("application/json");
            return gson.toJson(Map.of(
                "success", true,
                "strategy", strategyName,
                "symbol", symbol,
                "timeframe", timeframe,
                "total_trades", result.getTotalTrades(),
                "winning_trades", result.getWinningTrades(),
                "losing_trades", result.getLosingTrades(),
                "win_rate", result.getWinRate(),
                "total_return", result.getTotalReturn(),
                "max_drawdown", result.getMaxDrawdown(),
                "sharpe_ratio", result.getSharpeRatio(),
                "profit_factor", result.getProfitFactor()
            ));
        } catch (Exception e) {
            res.status(500);
            return gson.toJson(Map.of(
                "success", false,
                "error", e.getMessage()
            ));
        }
    }

    private String listStrategies(spark.Request req, spark.Response res) {
        res.type("application/json");
        return gson.toJson(strategies.keySet());
    }

    public void stop() {
        Spark.stop();
        System.out.println("Backtesting Engine stopped");
    }

    public static void main(String[] args) {
        BacktestingEngine engine = new BacktestingEngine();
        engine.start(8085);

        // Graceful shutdown
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutting down...");
            engine.stop();
        }));
    }
}
