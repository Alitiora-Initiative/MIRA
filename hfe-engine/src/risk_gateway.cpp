#include "risk_gateway.hpp"
#include <iostream>

namespace mira {
namespace hfe {

RiskGateway::RiskGateway()
    : max_position_size_(100000.0),
      max_leverage_(10.0),
      max_daily_loss_(10000.0),
      daily_pnl_(0.0) {
}

RiskGateway::~RiskGateway() {
}

bool RiskGateway::checkPreTradeRisk(const Order& order) {
    std::lock_guard<std::mutex> lock(risk_mutex_);

    // Check position size
    if (order.quantity * order.price > max_position_size_) {
        std::cout << "Risk check failed: Position size exceeds limit" << std::endl;
        return false;
    }

    // Check leverage (for perpetuals)
    if (order.leverage > max_leverage_) {
        std::cout << "Risk check failed: Leverage exceeds limit" << std::endl;
        return false;
    }

    // Check daily loss limit
    if (daily_pnl_ < -max_daily_loss_) {
        std::cout << "Risk check failed: Daily loss limit reached" << std::endl;
        return false;
    }

    // Check exposure
    double total_exposure = calculateTotalExposure(order.symbol);
    if (total_exposure + (order.quantity * order.price) > max_position_size_ * 2) {
        std::cout << "Risk check failed: Total exposure exceeds limit" << std::endl;
        return false;
    }

    return true;
}

void RiskGateway::updatePnL(double pnl) {
    std::lock_guard<std::mutex> lock(risk_mutex_);
    daily_pnl_ += pnl;
    std::cout << "Updated P&L: " << daily_pnl_ << std::endl;
}

void RiskGateway::resetDailyPnL() {
    std::lock_guard<std::mutex> lock(risk_mutex_);
    daily_pnl_ = 0.0;
    std::cout << "Daily P&L reset" << std::endl;
}

double RiskGateway::getDailyPnL() const {
    std::lock_guard<std::mutex> lock(risk_mutex_);
    return daily_pnl_;
}

void RiskGateway::setMaxPositionSize(double max_size) {
    std::lock_guard<std::mutex> lock(risk_mutex_);
    max_position_size_ = max_size;
}

void RiskGateway::setMaxLeverage(double max_leverage) {
    std::lock_guard<std::mutex> lock(risk_mutex_);
    max_leverage_ = max_leverage;
}

void RiskGateway::setMaxDailyLoss(double max_loss) {
    std::lock_guard<std::mutex> lock(risk_mutex_);
    max_daily_loss_ = max_loss;
}

double RiskGateway::calculateTotalExposure(const std::string& symbol) {
    // Simplified exposure calculation
    // In production, this would sum up all open positions
    return 0.0;
}

void RiskGateway::addPosition(const Position& position) {
    std::lock_guard<std::mutex> lock(risk_mutex_);
    positions_[position.symbol] = position;
}

Position RiskGateway::getPosition(const std::string& symbol) const {
    std::lock_guard<std::mutex> lock(risk_mutex_);
    auto it = positions_.find(symbol);
    if (it != positions_.end()) {
        return it->second;
    }
    return Position{};
}

} // namespace hfe
} // namespace mira
