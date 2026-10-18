#include "execution.hpp"
#include "market_data.hpp"
#include "risk_gateway.hpp"
#include <chrono>
#include <csignal>
#include <iostream>
#include <thread>

using namespace mira::hfe;

// Global flag for graceful shutdown
volatile sig_atomic_t shutdown_flag = 0;

void signalHandler(int signal) {
    std::cout << "\nReceived signal " << signal << ", shutting down..." << std::endl;
    shutdown_flag = 1;
}

int main() {
    // Set up signal handlers
    std::signal(SIGINT, signalHandler);
    std::signal(SIGTERM, signalHandler);

    std::cout << "=== MIRA High-Frequency Execution Engine ===" << std::endl;
    std::cout << "Starting components..." << std::endl;

    // Initialize components
    ExecutionEngine execution_engine;
    MarketDataHandler market_data;
    RiskGateway risk_gateway;

    // Configure risk gateway
    risk_gateway.setMaxPositionSize(100000.0);
    risk_gateway.setMaxLeverage(10.0);
    risk_gateway.setMaxDailyLoss(10000.0);

    // Start components
    execution_engine.start();
    market_data.start();

    std::cout << "All components started successfully" << std::endl;
    std::cout << "Engine ready for orders..." << std::endl;

    // Main loop
    int counter = 0;
    while (!shutdown_flag) {
        // Simulate order submission every 5 seconds
        if (counter % 50 == 0) {
            Order order;
            order.order_id = "ord_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
            order.symbol = "BTCUSDT";
            order.side = (counter % 100 == 0) ? OrderSide::BUY : OrderSide::SELL;
            order.quantity = 0.1;
            order.price = market_data.getMidPrice();
            order.status = OrderStatus::PENDING;
            order.submission_time = std::chrono::system_clock::now();
            order.leverage = 1.0;

            // Check risk
            if (risk_gateway.checkPreTradeRisk(order)) {
                execution_engine.submitOrder(order);
            } else {
                std::cout << "Order rejected by risk gateway" << std::endl;
            }
        }

        // Print status every 10 seconds
        if (counter % 100 == 0) {
            auto order_book = market_data.getOrderBook();
            auto open_orders = execution_engine.getOpenOrders();
            auto daily_pnl = risk_gateway.getDailyPnL();

            std::cout << "\n=== Status Update ===" << std::endl;
            std::cout << "Bid: " << order_book.bid_price << " (" << order_book.bid_quantity << ")" << std::endl;
            std::cout << "Ask: " << order_book.ask_price << " (" << order_book.ask_quantity << ")" << std::endl;
            std::cout << "Open Orders: " << open_orders.size() << std::endl;
            std::cout << "Daily P&L: " << daily_pnl << std::endl;
            std::cout << "==================\n" << std::endl;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        counter++;
    }

    // Shutdown
    std::cout << "Shutting down components..." << std::endl;
    execution_engine.stop();
    market_data.stop();

    std::cout << "HFE Engine shutdown complete" << std::endl;
    return 0;
}
