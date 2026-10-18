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
            Map<String, String> healthMap = new HashMap<>();
            healthMap.put("status", "healthy");
            return gson.toJson(healthMap);
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
                Map<String, Object> errorMap = new HashMap<>();
                errorMap.put("success", false);
                errorMap.put("error", "Strategy not found: " + strategyName);
                return gson.toJson(errorMap);
            }

            // Load data
            var data = dataStore.loadHistoricalData(symbol, timeframe, limit);
            if (data == null || data.isEmpty()) {
                res.status(400);
                Map<String, Object> errorMap2 = new HashMap<>();
                errorMap2.put("success", false);
                errorMap2.put("error", "No data available for symbol: " + symbol);
                return gson.toJson(errorMap2);
            }

            // Run backtest
            var result = strategy.runBacktest(data);

            res.type("application/json");
            Map<String, Object> responseMap = new HashMap<>();
            responseMap.put("success", true);
            responseMap.put("strategy", strategyName);
            responseMap.put("symbol", symbol);
            responseMap.put("timeframe", timeframe);
            responseMap.put("total_trades", result.getTotalTrades());
            responseMap.put("winning_trades", result.getWinningTrades());
            responseMap.put("losing_trades", result.getLosingTrades());
            responseMap.put("win_rate", result.getWinRate());
            responseMap.put("total_return", result.getTotalReturn());
            responseMap.put("max_drawdown", result.getMaxDrawdown());
            responseMap.put("sharpe_ratio", result.getSharpeRatio());
            responseMap.put("profit_factor", result.getProfitFactor());
            return gson.toJson(responseMap);
        } catch (Exception e) {
            res.status(500);
            Map<String, Object> errorMap3 = new HashMap<>();
            errorMap3.put("success", false);
            errorMap3.put("error", e.getMessage());
            return gson.toJson(errorMap3);
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
