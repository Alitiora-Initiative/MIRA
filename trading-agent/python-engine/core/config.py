"""
Configuration management for MIRA trading agent.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class GeneralConfig:
    log_level: str = "INFO"
    environment: str = "devnet"
    timezone: str = "UTC"


@dataclass
class SolanaConfig:
    rpc_endpoint: str
    commitment: str = "confirmed"
    jito_endpoint: str = ""
    jito_tip_lamports: int = 1000
    dexscreener_api_key: str = ""
    birdeye_api_key: str = ""


@dataclass
class TradingConfig:
    max_position_size: float = 0.1
    max_daily_loss: float = 0.05
    max_open_positions: int = 5
    sol: Dict[str, Any] = field(default_factory=dict)
    assets: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhiMatrixConfig:
    liquidity_density_weight: float = 0.50
    holder_concentration_weight: float = 0.30
    volumetric_velocity_weight: float = 0.20
    minimum_phi_score: float = 85.0
    tvl_baseline_usd: float = 10000


@dataclass
class RiskManagementConfig:
    position_sizing_method: str = "kelly_criterion"
    max_drawdown: float = 0.20
    leverage: float = 1.0
    diversification_threshold: float = 0.3
    take_profit_floor: float = 0.10
    take_profit_cap: float = 10.0
    stop_loss_floor: float = -0.10
    stop_loss_ceiling: float = -0.40


@dataclass
class MPCConfig:
    threshold: int = 2
    total_shares: int = 3
    local_share_path: str = ""
    cloud_endpoint: str = ""
    biometric_required: bool = True


@dataclass
class ScalingConfig:
    milestone_target_sol: int = 10
    subagent_genesis_profit_usd: float = 20.0
    subagent_count: int = 10
    subagent_funding_usd: float = 1.0
    perpetual_scaling_threshold_usd: float = 200.0
    perpetual_execution_schedule: list = field(default_factory=list)


@dataclass
class SubagentConfig:
    base_image: str = "alpine"
    memory_limit_mb: int = 128
    cpu_limit: float = 0.25


@dataclass
class DatabaseConfig:
    type: str = "sqlite"
    connection_string: str = "sqlite:///trading_data.db"


@dataclass
class WalletServiceConfig:
    grpc_endpoint: str = "localhost:50051"
    ws_endpoint: str = "ws://localhost:8080"
    biometric_timeout_seconds: int = 300
    hardware_wallet_required: bool = False


@dataclass
class MevEngineConfig:
    enabled: bool = True
    grpc_endpoint: str = "localhost:50052"
    private_mempool: str = "jito"
    max_slippage_bps: int = 300
    sandwich_detection: bool = True
    circuit_breaker_enabled: bool = True


@dataclass
class AccountModeConfig:
    mode: str = "demo"  # demo or live
    demo: Dict[str, Any] = field(default_factory=dict)
    live: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataPipelineConfig:
    go_indexer: Dict[str, Any] = field(default_factory=dict)
    hfe_engine: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsConfig:
    julia: Dict[str, Any] = field(default_factory=dict)
    r: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Config:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    solana: SolanaConfig = field(default_factory=SolanaConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    phi_matrix: PhiMatrixConfig = field(default_factory=PhiMatrixConfig)
    risk_management: RiskManagementConfig = field(default_factory=RiskManagementConfig)
    mpc: MPCConfig = field(default_factory=MPCConfig)
    scaling: ScalingConfig = field(default_factory=ScalingConfig)
    subagent: SubagentConfig = field(default_factory=SubagentConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    wallet_service: WalletServiceConfig = field(default_factory=WalletServiceConfig)
    mev_engine: MevEngineConfig = field(default_factory=MevEngineConfig)
    account_mode: AccountModeConfig = field(default_factory=AccountModeConfig)
    data_pipeline: DataPipelineConfig = field(default_factory=DataPipelineConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
