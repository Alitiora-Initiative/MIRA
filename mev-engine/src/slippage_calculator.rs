use anyhow::Result;

/// Calculates optimal slippage protection
pub struct SlippageCalculator {
    base_slippage_bps: u32,
    max_slippage_bps: u32,
}

impl SlippageCalculator {
    pub fn new(base_slippage_bps: u32, max_slippage_bps: u32) -> Self {
        Self {
            base_slippage_bps,
            max_slippage_bps,
        }
    }

    /// Calculate recommended slippage based on pool characteristics
    pub fn calculate_slippage(
        &self,
        pool_tvl_usd: f64,
        amount_usd: f64,
        liquidity_depth_ratio: f64,
    ) -> (u32, f64) {
        // Higher slippage for smaller pools or larger trades
        let size_ratio = amount_usd / pool_tvl_usd;
        let mut recommended_slippage = self.base_slippage_bps;

        // Adjust based on trade size relative to pool
        if size_ratio > 0.01 {
            // Trade is > 1% of pool TVL
            recommended_slippage = (recommended_slippage as f64 * (1.0 + size_ratio * 100.0)) as u32;
        }

        // Adjust based on liquidity depth
        if liquidity_depth_ratio < 0.5 {
            // Shallow liquidity
            recommended_slippage = (recommended_slippage as f64 * 1.5) as u32;
        }

        // Cap at maximum
        recommended_slippage = recommended_slippage.min(self.max_slippage_bps);

        // Estimate price impact (simplified)
        let price_impact = (size_ratio * 100.0).min(50.0); // Cap at 50%

        (recommended_slippage, price_impact)
    }

    /// Check if slippage is acceptable
    pub fn is_acceptable(&self, slippage_bps: u32, max_allowed_bps: u32) -> bool {
        slippage_bps <= max_allowed_bps
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_slippage_calculation() {
        let calculator = SlippageCalculator::new(100, 500);

        let (slippage, impact) = calculator.calculate_slippage(10000.0, 100.0, 0.8);
        assert!(slippage >= 100);
        assert!(impact < 5.0);
    }

    #[test]
    fn test_large_trade_slippage() {
        let calculator = SlippageCalculator::new(100, 500);

        let (slippage, impact) = calculator.calculate_slippage(10000.0, 500.0, 0.3);
        assert!(slippage > 100);
        assert!(impact > 0.0);
    }
}
