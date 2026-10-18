use anyhow::Result;
use mira_mev_engine::{CircuitBreaker, SandwichDetector, SlippageCalculator};
use std::net::SocketAddr;
use tonic::transport::Server;
use tonic::{Request, Response, Status};
use tracing::{info, warn};
use tracing_subscriber;

mod mev {
    tonic::include_proto!("mev");
}

use mev::{mev_service_server::{MevService, MevServiceServer}, *};

pub struct MyMevService {
    sandwich_detector: SandwichDetector,
    slippage_calculator: SlippageCalculator,
    circuit_breaker: CircuitBreaker,
}

impl MyMevService {
    pub fn new() -> Self {
        Self {
            sandwich_detector: SandwichDetector::new(60),
            slippage_calculator: SlippageCalculator::new(100, 500),
            circuit_breaker: CircuitBreaker::new(3, 60),
        }
    }
}

#[tonic::async_trait]
impl MevService for MyMevService {
    async fn check_safety(
        &self,
        request: Request<SafetyCheckRequest>,
    ) -> Result<Response<SafetyCheckResponse>, Status> {
        let req = request.into_inner();

        info!("Checking safety for pool: {}", req.pool_address);

        // Check circuit breaker
        if let Err(e) = self.circuit_breaker.check_execution(&req.pool_address, 100) {
            return Ok(Response::new(SafetyCheckResponse {
                is_safe: false,
                warnings: vec![e.to_string()],
                risk_level: "high".to_string(),
                risk_score: 0.9,
            }));
        }

        // Check for sandwich attacks
        let (is_vulnerable, warnings) = self.sandwich_detector.check_vulnerability(
            &req.pool_address,
            req.amount as u64,
        );

        let risk_level = if is_vulnerable {
            "high"
        } else if warnings.is_empty() {
            "low"
        } else {
            "medium"
        };

        let risk_score = if is_vulnerable { 0.8 } else { 0.2 };

        Ok(Response::new(SafetyCheckResponse {
            is_safe: !is_vulnerable,
            warnings,
            risk_level: risk_level.to_string(),
            risk_score,
        }))
    }

    async fn optimize_slippage(
        &self,
        request: Request<SlippageRequest>,
    ) -> Result<Response<SlippageResponse>, Status> {
        let req = request.into_inner();

        info!("Optimizing slippage for pool: {}", req.pool_address);

        // Simplified calculation - in production, fetch real pool data
        let pool_tvl_usd = 10000.0;
        let amount_usd = req.amount as f64 / 1e9; // Convert lamports to USD (simplified)
        let liquidity_depth_ratio = 0.8;

        let (recommended_slippage, price_impact) = self
            .slippage_calculator
            .calculate_slippage(pool_tvl_usd, amount_usd, liquidity_depth_ratio);

        let is_acceptable = self
            .slippage_calculator
            .is_acceptable(recommended_slippage, req.max_slippage_bps as u32);

        Ok(Response::new(SlippageResponse {
            recommended_slippage_bps: recommended_slippage as i32,
            expected_price_impact: price_impact,
            estimated_gas_cost: 0.0005, // Simplified
            is_acceptable,
        }))
    }

    async fn bundle_transactions(
        &self,
        request: Request<BundleRequest>,
    ) -> Result<Response<BundleResponse>, Status> {
        let req = request.into_inner();

        info!("Bundling {} transactions", req.transactions.len());

        // In production, this would send to Jito or similar
        let bundle_id = format!("bundle_{}", uuid::Uuid::new_v4());

        Ok(Response::new(BundleResponse {
            success: true,
            bundle_id,
            error: String::new(),
        }))
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt::init();

    let addr: SocketAddr = "[::1]:50052".parse()?;
    let mev_service = MyMevService::new();

    info!("MEV Engine gRPC server listening on {}", addr);

    Server::builder()
        .add_service(MevServiceServer::new(mev_service))
        .serve(addr)
        .await?;

    Ok(())
}
