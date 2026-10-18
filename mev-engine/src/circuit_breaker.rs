use anyhow::Result;
use dashmap::DashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

/// Safety circuit breaker to prevent catastrophic errors
pub struct CircuitBreaker {
    failure_counts: DashMap<String, FailureStats>,
    is_global_halted: AtomicBool,
    max_failures: u32,
    reset_after: Duration,
}

#[derive(Clone, Debug)]
struct FailureStats {
    count: u32,
    last_failure: Instant,
}

impl CircuitBreaker {
    pub fn new(max_failures: u32, reset_after_secs: u64) -> Self {
        Self {
            failure_counts: DashMap::new(),
            is_global_halted: AtomicBool::new(false),
            max_failures,
            reset_after: Duration::from_secs(reset_after_secs),
        }
    }

    /// Record a failure for a contract
    pub fn record_failure(&self, contract_address: String) {
        let mut should_halt = false;

        self.failure_counts
            .entry(contract_address.clone())
            .and_modify(|stats| {
                // Reset if enough time has passed
                if stats.last_failure.elapsed() > self.reset_after {
                    stats.count = 0;
                }
                stats.count += 1;
                stats.last_failure = Instant::now();

                if stats.count >= self.max_failures {
                    should_halt = true;
                }
            })
            .or_insert_with(|| FailureStats {
                count: 1,
                last_failure: Instant::now(),
            });

        if should_halt {
            tracing::warn!("Circuit breaker triggered for contract: {}", contract_address);
        }
    }

    /// Check if a contract is halted
    pub fn is_halted(&self, contract_address: &str) -> bool {
        if self.is_global_halted.load(Ordering::Relaxed) {
            return true;
        }

        if let Some(stats) = self.failure_counts.get(contract_address) {
            // Reset if enough time has passed
            if stats.last_failure.elapsed() > self.reset_after {
                return false;
            }
            return stats.count >= self.max_failures;
        }

        false
    }

    /// Check if execution should proceed
    pub fn check_execution(&self, contract_address: &str, slippage_bps: u32) -> Result<()> {
        // Check circuit breaker
        if self.is_halted(contract_address) {
            anyhow::bail!("Contract is halted by circuit breaker");
        }

        // Check slippage guardrail
        if slippage_bps > 500 {
            // 5% slippage
            anyhow::bail!("Slippage too high: {} bps", slippage_bps);
        }

        Ok(())
    }

    /// Record a success (can reset failure count)
    pub fn record_success(&self, contract_address: String) {
        if let Some(mut stats) = self.failure_counts.get_mut(&contract_address) {
            stats.count = stats.count.saturating_sub(1);
        }
    }

    /// Halt all operations globally
    pub fn global_halt(&self) {
        self.is_global_halted.store(true, Ordering::Relaxed);
        tracing::error!("Global circuit breaker triggered!");
    }

    /// Resume all operations
    pub fn global_resume(&self) {
        self.is_global_halted.store(false, Ordering::Relaxed);
        tracing::info!("Global circuit breaker resumed");
    }

    /// Reset a specific contract
    pub fn reset_contract(&self, contract_address: &str) {
        self.failure_counts.remove(contract_address);
        tracing::info!("Circuit breaker reset for contract: {}", contract_address);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_circuit_breaker() {
        let breaker = CircuitBreaker::new(3, 60);

        let contract = "test_contract".to_string();

        // Record failures
        for _ in 0..3 {
            breaker.record_failure(contract.clone());
        }

        assert!(breaker.is_halted(&contract));

        // Reset
        breaker.reset_contract(&contract);
        assert!(!breaker.is_halted(&contract));
    }
}
