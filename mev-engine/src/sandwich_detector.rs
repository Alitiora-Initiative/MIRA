use anyhow::Result;
use dashmap::DashMap;
use std::time::{Duration, Instant};

/// Detects potential sandwich attacks on memecoin pools
pub struct SandwichDetector {
    recent_txs: DashMap<String, Vec<TransactionInfo>>,
    window: Duration,
}

#[derive(Clone, Debug)]
struct TransactionInfo {
    tx_hash: String,
    timestamp: Instant,
    amount: u64,
    pool_address: String,
}

impl SandwichDetector {
    pub fn new(window_secs: u64) -> Self {
        Self {
            recent_txs: DashMap::new(),
            window: Duration::from_secs(window_secs),
        }
    }

    /// Add a transaction to the detector
    pub fn add_transaction(&self, tx_hash: String, pool_address: String, amount: u64) {
        let info = TransactionInfo {
            tx_hash: tx_hash.clone(),
            timestamp: Instant::now(),
            amount,
            pool_address,
        };

        self.recent_txs
            .entry(pool_address.clone())
            .and_modify(|txs| {
                txs.push(info.clone());
                // Keep only recent transactions
                txs.retain(|t| t.timestamp.elapsed() < self.window);
            })
            .or_insert_with(|| vec![info]);
    }

    /// Check if a transaction is vulnerable to sandwich attack
    pub fn check_vulnerability(&self, pool_address: &str, amount: u64) -> (bool, Vec<String>) {
        let mut warnings = Vec::new();
        let mut is_vulnerable = false;

        if let Some(txs) = self.recent_txs.get(pool_address) {
            // Check for large recent transactions
            for tx in txs.iter() {
                if tx.amount > amount * 10 {
                    warnings.push(format!(
                        "Large transaction detected recently in pool: {}",
                        tx.tx_hash
                    ));
                    is_vulnerable = true;
                }
            }

            // Check for rapid succession
            if txs.len() > 5 {
                warnings.push("High transaction frequency detected in pool".to_string());
                is_vulnerable = true;
            }
        }

        (is_vulnerable, warnings)
    }

    /// Clean up old transactions
    pub fn cleanup(&self) {
        for mut entry in self.recent_txs.iter_mut() {
            entry
                .value_mut()
                .retain(|t| t.timestamp.elapsed() < self.window);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sandwich_detection() {
        let detector = SandwichDetector::new(60);
        detector.add_transaction("tx1".to_string(), "pool1".to_string(), 1000);

        let (vulnerable, warnings) = detector.check_vulnerability("pool1", 100);
        assert!(vulnerable);
        assert!(!warnings.is_empty());
    }
}
