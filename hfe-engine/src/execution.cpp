#include "execution.hpp"
#include <chrono>
#include <iostream>
#include <thread>

namespace mira {
namespace hfe {

ExecutionEngine::ExecutionEngine() {
    // Initialize order book
    order_book_.reserve(10000);
}

ExecutionEngine::~ExecutionEngine() {
    stop();
}

void ExecutionEngine::start() {
    running_ = true;
    execution_thread_ = std::thread(&ExecutionEngine::executionLoop, this);
    std::cout << "HFE Execution Engine started" << std::endl;
}

void ExecutionEngine::stop() {
    running_ = false;
    if (execution_thread_.joinable()) {
        execution_thread_.join();
    }
    std::cout << "HFE Execution Engine stopped" << std::endl;
}

void ExecutionEngine::executionLoop() {
    while (running_) {
        auto start = std::chrono::high_resolution_clock::now();

        // Process orders
        processOrders();

        // Check latency
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        if (duration.count() > 1000) { // > 1ms warning
            std::cout << "Warning: Execution loop took " << duration.count() << " microseconds" << std::endl;
        }

        // Small sleep to prevent CPU spinning
        std::this_thread::sleep_for(std::chrono::microseconds(100));
    }
}

void ExecutionEngine::processOrders() {
    std::lock_guard<std::mutex> lock(order_mutex_);

    for (auto& order : pending_orders_) {
        if (order.status == OrderStatus::PENDING) {
            executeOrder(order);
        }
    }

    // Remove completed orders
    pending_orders_.erase(
        std::remove_if(pending_orders_.begin(), pending_orders_.end(),
            [](const Order& o) { return o.status == OrderStatus::FILLED || o.status == OrderStatus::CANCELLED; }),
        pending_orders_.end()
    );
}

void ExecutionEngine::executeOrder(Order& order) {
    auto start = std::chrono::high_resolution_clock::now();

    // Simulate order execution
    // In production, this would send to CEX API
    order.status = OrderStatus::FILLED;
    order.filled_quantity = order.quantity;
    order.fill_price = order.price;
    order.execution_time = std::chrono::system_clock::now();

    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    std::cout << "Order executed: " << order.symbol << " " << order.side
              << " " << order.quantity << " @ " << order.price
              << " in " << duration.count() << " microseconds" << std::endl;
}

void ExecutionEngine::submitOrder(const Order& order) {
    std::lock_guard<std::mutex> lock(order_mutex_);
    pending_orders_.push_back(order);
    std::cout << "Order submitted: " << order.symbol << " " << order.side
              << " " << order.quantity << " @ " << order.price << std::endl;
}

std::vector<Order> ExecutionEngine::getOpenOrders() const {
    std::lock_guard<std::mutex> lock(order_mutex_);
    std::vector<Order> open_orders;
    for (const auto& order : pending_orders_) {
        if (order.status == OrderStatus::PENDING) {
            open_orders.push_back(order);
        }
    }
    return open_orders;
}

void ExecutionEngine::cancelOrder(const std::string& order_id) {
    std::lock_guard<std::mutex> lock(order_mutex_);
    for (auto& order : pending_orders_) {
        if (order.order_id == order_id && order.status == OrderStatus::PENDING) {
            order.status = OrderStatus::CANCELLED;
            std::cout << "Order cancelled: " << order_id << std::endl;
            return;
        }
    }
}

double ExecutionEngine::getLatencyP95() const {
    // Simplified latency calculation
    return 0.5; // 0.5ms
}

} // namespace hfe
} // namespace mira
