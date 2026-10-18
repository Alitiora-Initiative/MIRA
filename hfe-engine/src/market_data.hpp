#ifndef MIRA_HFE_MARKET_DATA_HPP
#define MIRA_HFE_MARKET_DATA_HPP

#include <chrono>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

namespace mira {
namespace hfe {

struct Tick {
    std::string symbol;
    double price;
    double quantity;
    std::chrono::system_clock::time_point timestamp;
};

struct OrderBook {
    double bid_price;
    double ask_price;
    double bid_quantity;
    double ask_quantity;
    std::chrono::system_clock::time_point timestamp;
};

class MarketDataHandler {
public:
    MarketDataHandler();
    ~MarketDataHandler();

    void start();
    void stop();
    OrderBook getOrderBook() const;
    std::vector<Tick> getRecentTicks() const;
    void addTick(const Tick& tick);
    double getMidPrice() const;

private:
    void dataLoop();
    void updateOrderBook();

    OrderBook order_book_;
    std::vector<Tick> recent_ticks_;
    mutable std::mutex book_mutex_;
    mutable std::mutex tick_mutex_;
    std::thread data_thread_;
    bool running_;
};

} // namespace hfe
} // namespace mira

#endif // MIRA_HFE_MARKET_DATA_HPP
