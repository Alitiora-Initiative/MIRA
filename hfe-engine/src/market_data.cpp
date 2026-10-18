#include "market_data.hpp"
#include <iostream>
#include <random>

namespace mira {
namespace hfe {

MarketDataHandler::MarketDataHandler() {
    // Initialize order book
    order_book_.bid_price = 0.0;
    order_book_.ask_price = 0.0;
    order_book_.bid_quantity = 0.0;
    order_book_.ask_quantity = 0.0;
}

MarketDataHandler::~MarketDataHandler() {
    stop();
}

void MarketDataHandler::start() {
    running_ = true;
    data_thread_ = std::thread(&MarketDataHandler::dataLoop, this);
    std::cout << "Market Data Handler started" << std::endl;
}

void MarketDataHandler::stop() {
    running_ = false;
    if (data_thread_.joinable()) {
        data_thread_.join();
    }
    std::cout << "Market Data Handler stopped" << std::endl;
}

void MarketDataHandler::dataLoop() {
    while (running_) {
        // Simulate market data updates
        updateOrderBook();

        // Small sleep
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

void MarketDataHandler::updateOrderBook() {
    std::lock_guard<std::mutex> lock(book_mutex_);

    // Simulate price movements
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> price_dist(99.0, 101.0);
    std::uniform_real_distribution<> qty_dist(1000.0, 5000.0);

    order_book_.bid_price = price_dist(gen);
    order_book_.ask_price = order_book_.bid_price + 0.01;
    order_book_.bid_quantity = qty_dist(gen);
    order_book_.ask_quantity = qty_dist(gen);
    order_book_.timestamp = std::chrono::system_clock::now();
}

OrderBook MarketDataHandler::getOrderBook() const {
    std::lock_guard<std::mutex> lock(book_mutex_);
    return order_book_;
}

std::vector<Tick> MarketDataHandler::getRecentTicks() const {
    std::lock_guard<std::mutex> lock(tick_mutex_);
    return recent_ticks_;
}

void MarketDataHandler::addTick(const Tick& tick) {
    std::lock_guard<std::mutex> lock(tick_mutex_);
    recent_ticks_.push_back(tick);

    // Keep only last 1000 ticks
    if (recent_ticks_.size() > 1000) {
        recent_ticks_.erase(recent_ticks_.begin());
    }
}

double MarketDataHandler::getMidPrice() const {
    std::lock_guard<std::mutex> lock(book_mutex_);
    return (order_book_.bid_price + order_book_.ask_price) / 2.0;
}

} // namespace hfe
} // namespace mira
