#ifndef MIRA_HFE_RISK_GATEWAY_HPP
#define MIRA_HFE_RISK_GATEWAY_HPP

#include "execution.hpp"
#include <map>
#include <mutex>
#include <string>

namespace mira {
namespace hfe {

struct Position {
    std::string symbol;
    double quantity;
    double entry_price;
    double current_price;
    double unrealized_pnl;
};

class RiskGateway {
public:
    RiskGateway();
    ~RiskGateway();

    bool checkPreTradeRisk(const Order& order);
    void updatePnL(double pnl);
    void resetDailyPnL();
    double getDailyPnL() const;

    void setMaxPositionSize(double max_size);
    void setMaxLeverage(double max_leverage);
    void setMaxDailyLoss(double max_loss);

    void addPosition(const Position& position);
    Position getPosition(const std::string& symbol) const;

private:
    double calculateTotalExposure(const std::string& symbol);

    double max_position_size_;
    double max_leverage_;
    double max_daily_loss_;
    double daily_pnl_;
    std::map<std::string, Position> positions_;
    mutable std::mutex risk_mutex_;
};

} // namespace hfe
} // namespace mira

#endif // MIRA_HFE_RISK_GATEWAY_HPP
