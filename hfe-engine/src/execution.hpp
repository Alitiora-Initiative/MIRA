#ifndef MIRA_HFE_EXECUTION_HPP
#define MIRA_HFE_EXECUTION_HPP

#include <chrono>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

namespace mira {
namespace hfe {

enum class OrderSide { BUY, SELL };
enum class OrderStatus { PENDING, FILLED, CANCELLED, REJECTED };

struct Order {
    std::string order_id;
    std::string symbol;
    OrderSide side;
    double quantity;
    double price;
    OrderStatus status;
    double filled_quantity;
    double fill_price;
    std::chrono::system_clock::time_point submission_time;
    std::chrono::system_clock::time_point execution_time;
};

class ExecutionEngine {
public:
    ExecutionEngine();
    ~ExecutionEngine();

    void start();
    void stop();
    void submitOrder(const Order& order);
    void cancelOrder(const std::string& order_id);
    std::vector<Order> getOpenOrders() const;
    double getLatencyP95() const;

private:
    void executionLoop();
    void processOrders();
    void executeOrder(Order& order);

    std::vector<Order> pending_orders_;
    std::vector<Order> order_book_;
    mutable std::mutex order_mutex_;
    std::thread execution_thread_;
    bool running_;
};

} // namespace hfe
} // namespace mira

#endif // MIRA_HFE_EXECUTION_HPP
