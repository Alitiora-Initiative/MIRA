# MIRA - Multi-Language Autonomous Trading Agent

MIRA is an enterprise-grade, autonomous AI trading agent designed for memecoins, tokenized stocks, and perpetual contracts across multiple blockchains (Solana, EVM) and centralized exchanges.

## Architecture Overview

MIRA uses a multi-language microservices architecture, leveraging each language for its specific industry strengths:

- **Python**: Core AI orchestration, LLM agents, deep learning models
- **TypeScript**: Wallet state management, secure signing, dashboard UI
- **Rust**: MEV protection, memory-safe execution, circuit breakers
- **Go**: High-concurrency blockchain indexing, data ingestion
- **C++**: Ultra-low latency execution for CEX perps
- **Julia**: High-performance portfolio optimization, risk simulation
- **R**: Statistical modeling, econometrics, volatility forecasting
- **Java**: Enterprise backtesting, broker API integration
- **SQL**: Transaction logging, asset registry, performance metrics
- **Pine Script**: TradingView webhook indicators
- **MQL4/MQL5**: MetaTrader execution bridges

## Current Status

### ✅ Phase 1: Wallet & Web3 Execution Layer (COMPLETE)

**Components Implemented:**

1. **TypeScript Wallet Service** (`wallet-service/`)
   - Wallet state manager with session management
   - Biometric token generation for secure signing
   - gRPC server for transaction signing
   - WebSocket gateway for real-time updates
   - Hardware wallet support framework

2. **Rust MEV Engine** (`mev-engine/`)
   - Sandwich attack detection
   - Slippage optimization calculator
   - Circuit breaker for safety
   - gRPC service for safety checks

3. **Python Integration** (`python-engine/wallet/`)
   - gRPC client for wallet service
   - Seamless integration with existing exchange manager

**Features:**
- Demo/Live account modes
- Secure wallet signing without plain-text private keys
- MEV protection for memecoin trading
- Real-time WebSocket updates

### ✅ Phase 2: Data Ingestion Pipeline (COMPLETE)

**Components Implemented:**

1. **Go Blockchain Indexer** (`data-pipeline/indexer/`)
   - Concurrent WebSocket connections to RPC nodes
   - Real-time blockchain event streaming
   - Transfer and swap event detection
   - Kafka integration for data streaming
   - Automatic reconnection with exponential backoff

2. **Go Data Normalizer** (`data-pipeline/normalizer/`)
   - Multi-chain data normalization
   - Unified asset identification
   - Kafka consumer/producer pattern
   - Schema validation

3. **Go Mempool Monitor** (`data-pipeline/mempool/`)
   - Pending transaction monitoring
   - Front-running detection
   - Flash loan opportunity detection
   - Gas price analysis

4. **C++ HFE Execution Engine** (`hfe-engine/`)
   - Ultra-low latency order execution (< 1ms target)
   - Market data handler with order book reconstruction
   - Risk gateway with pre-trade checks
   - Position management
   - Lock-free data structures

5. **Infrastructure** (`docker-compose.yml`)
   - Apache Kafka for message bus
   - Zookeeper for Kafka coordination
   - Kafka UI for monitoring
   - PostgreSQL for data storage
   - Redis for caching

**Features:**
- High-concurrency data ingestion
- Real-time order book updates
- Sub-millisecond execution latency
- Automatic failure recovery
- Scalable microservices architecture

### ✅ Phase 3: Enhanced Analytics Layer (COMPLETE)

**Components Implemented:**

1. **Julia Portfolio Optimizer** (`analytics-julia/src/portfolio_optimizer.jl`)
   - Mean-variance optimization using JuMP and HiGHS
   - CVaR (Conditional Value at Risk) optimization
   - Convex optimization for portfolio weights
   - Maximum position constraints
   - HTTP API for optimization requests

2. **Julia Risk Simulation Engine** (`analytics-julia/src/risk_simulation.jl`)
   - Monte Carlo simulation for portfolio VaR
   - Geometric Brownian Motion (GBM) simulation
   - Scenario analysis and stress testing
   - Expected Shortfall (CVaR) calculation
   - Correlated random number generation

3. **R Statistical Modeling Service** (`analytics-r/src/statistical_modeling.R`)
   - GARCH volatility forecasting (using rugarch)
   - ARIMA time-series forecasting
   - Cointegration testing
   - Granger causality testing
   - Quantile regression
   - Historical VaR calculation

4. **R Liquidity Pool Analytics** (`analytics-r/src/pool_analytics.R`)
   - Pool dynamics analysis
   - Impermanent loss calculation
   - Slippage modeling
   - Pool depth forecasting
   - Constant product AMM analysis

5. **Python Integration** (`python-engine/analytics/`)
   - Julia analytics HTTP client
   - R analytics HTTP client
   - Async API calls for non-blocking operation
   - Result parsing and integration

**Features:**
- High-performance portfolio optimization
- Advanced volatility forecasting
- Statistical arbitrage detection
- Cross-asset correlation modeling
- Liquidity pool analytics for memecoins

### ✅ Phase 4: Enterprise Backtesting (COMPLETE)

**Components Implemented:**

1. **Java Backtesting Engine** (`backtesting-java/`)
   - Spark Java HTTP server for API
   - Data store for historical OHLCV data
   - Strategy framework with Φ Matrix implementation
   - Performance metrics calculation (Sharpe, Sortino, etc.)
   - Maven build system

2. **Φ Matrix Strategy** (`backtesting-java/src/main/java/com/mira/backtesting/strategy/PhiMatrixStrategy.java`)
   - Simulates Φ Matrix filtering in backtesting
   - Calculates synthetic Φ scores
   - Trade execution simulation
   - Performance metrics tracking

**Features:**
- Enterprise-grade backtesting framework
- Strategy composition support
- Synthetic data generation for testing
- HTTP API for backtesting requests
- Performance metrics calculation

### ✅ Phase 5: External Bridges (COMPLETE)

**Components Implemented:**

1. **Database Schema** (`database/schema.sql`)
   - Asset registry for multi-asset support
   - On-chain transaction logging
   - Wallet balance tracking
   - Performance metrics storage
   - Webhook signal management

2. **Pine Script Indicators** (`pine-script/`)
   - Macro trend detector for TradingView
   - EMA crossover detection
   - Webhook integration for signals

3. **MQL5 Bridge** (`mql5/execution_bridge.mq5`)
   - MetaTrader 5 execution bridge
   - Signal forwarding to main system
   - Magic number support for order tracking

**Features:**
- Multi-asset database schema
- TradingView webhook integration
- MetaTrader bridge for Forex/CFD
- External signal ingestion

### ✅ Demo/Live Account Modes (COMPLETE)

**Components Implemented:**

1. **Account Manager** (`trading-agent/python-engine/account/`)
   - Demo mode with paper trading simulation
   - Live mode with validation and safety checks
   - Position tracking and P&L calculation
   - Trade history management
   - Balance management

2. **Configuration Integration**
   - Demo mode: paper trading with simulated balances
   - Live mode: real trading with biometric authentication
   - Position size limits
   - Daily loss limits
   - Account reset functionality

**Features:**
- Demo mode for testing strategies (no real funds)
- Live mode for production trading
- Paper trading simulation
- Real-time P&L tracking
- Trade history and analytics
- Safety checks for live trading

### 📋 Phase 3: Enhanced Analytics Layer (PENDING)

### 📋 Phase 4: Enterprise Backtesting (PENDING)

### 📋 Phase 5: External Bridges (PENDING)

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Rust 1.70+
- Docker (for infrastructure services)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Alitiora-Initiative/MIRA.git
cd MIRA
```

2. **Install Python dependencies**
```bash
cd trading-agent
pip install -r requirements.txt
```

3. **Install TypeScript dependencies**
```bash
cd wallet-service
npm install
```

4. **Build Rust MEV engine**
```bash
cd mev-engine
cargo build --release
```

5. **Configure environment**
```bash
cp trading-agent/config/config.example.yaml trading-agent/config/config.yaml
# Edit config.yaml with your API keys and settings
```

### Running the System

#### Demo Mode (Paper Trading)
```yaml
# In config.yaml
account_mode:
  mode: demo
  demo:
    paper_trading: true
    initial_balance_usd: 10000
```

#### Live Mode (Real Trading)
```yaml
# In config.yaml
account_mode:
  mode: live
  live:
    require_biometric: true
    max_position_size_usd: 1000
```

#### Start Services

1. **Start Wallet Service**
```bash
cd wallet-service
npm run build
npm start
```

2. **Start MEV Engine**
```bash
cd mev-engine
cargo run --release
```

3. **Start Python Trading Engine**
```bash
cd trading-agent/python-engine
python main.py
```

## Configuration

### Wallet Service
- `WALLET_GRPC_ENDPOINT`: gRPC server address (default: localhost:50051)
- `WS_PORT`: WebSocket port (default: 8080)
- `SOLANA_RPC_URL`: Solana RPC endpoint
- `EVM_RPC_URL`: EVM RPC endpoint (optional)

### MEV Engine
- `MEV_GRPC_ENDPOINT`: gRPC server address (default: localhost:50052)
- `MAX_SLIPPAGE_BPS`: Maximum allowed slippage (default: 300)
- `CIRCUIT_BREAKER_ENABLED`: Enable safety circuit breaker (default: true)

### Trading Engine
- `environment`: devnet or mainnet
- `trading.max_position_size`: Maximum position size as portfolio percentage
- `risk_management.max_drawdown`: Maximum allowed drawdown
- `phi_matrix.minimum_phi_score`: Minimum Φ score for token eligibility

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              TypeScript/TypeScript Dashboard                 │
│              (Real-time UI, Wallet State)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ WebSocket / gRPC
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python Core Orchestrator                  │
│        (AI Models, LLM Agents, General Logic)                │
└───────────────┬───────────────┬───────────────┬───────────────┘
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │   Rust Layer │ │ Go Layer  │ │ Julia Layer │
        │  (MEV Safety │ │(Data Ingest│ │ (Portfolio  │
        │   & Safety)  │ │  & RPC)   │ │ Optimization)│
        └───────┬──────┘ └─────┬─────┘ └──────┬──────┘
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │   C++ Layer  │ │  Java     │ │   R Layer   │
        │ (HFE Engine) │ │ (Backtest │ │ (Statistical│
        │              │ │  & Broker)│ │  Modeling)  │
        └──────────────┘ └───────────┘ └─────────────┘
```

## Security

- **No Plain-Text Private Keys**: All keys stored in HSM or encrypted vault
- **MPC Signing**: Multi-party computation for transaction signing
- **Biometric Authentication**: Required for live trading
- **MEV Protection**: Sandwich attack detection and private mempool routing
- **Circuit Breakers**: Automatic halt on failure thresholds

## Demo vs Live Trading

### Demo Mode
- Paper trading with simulated balances
- No real funds at risk
- Perfect for testing strategies
- Simulated slippage and execution

### Live Mode
- Real trading with actual funds
- Requires biometric authentication
- MEV protection enabled
- Hardware wallet support (optional)

## Development

### Running Tests
```bash
# Python tests
cd trading-agent
pytest

# TypeScript tests
cd wallet-service
npm test

# Rust tests
cd mev-engine
cargo test
```

### Building for Production
```bash
# TypeScript
cd wallet-service
npm run build

# Rust
cd mev-engine
cargo build --release

# Python (use PyInstaller for executable)
cd trading-agent
pyinstaller --onefile python-engine/main.py
```

## Deployment

### Docker Compose (Development)
```bash
docker-compose up -d
```

### Kubernetes (Production)
```bash
kubectl apply -f k8s/
```

### Vercel (Dashboard)
```bash
vercel --prod
```

The dashboard is deployed at: https://mira-trading-agent.vercel.app

### Quick Start (Demo Mode)
```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Start wallet service
cd wallet-service
npm install
npm start

# 3. Start MEV engine
cd ../mev-engine
cargo run --release

# 4. Start Python trading engine
cd ../trading-agent/python-engine
python main.py
```

### Quick Start (Live Mode)
Set `account_mode.mode: live` in config.yaml and ensure biometric authentication is configured.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/Alitiora-Initiative/MIRA/issues
- Documentation: See ARCHITECTURE_BLUEPRINT.md for detailed architecture

## Roadmap

- [x] Phase 1: Wallet & Web3 Execution Layer (TypeScript + Rust)
- [x] Phase 2: Data Ingestion Pipeline (Go + C++)
- [x] Phase 3: Enhanced Analytics Layer (Julia + R)
- [x] Phase 4: Enterprise Backtesting (Java)
- [x] Phase 5: External Bridges (SQL + Pine Script + MQL4/MQL5)
- [x] Demo/Live Account Modes
- [x] Dashboard & Deployment
- [x] Documentation & Configuration

## System Status

**All Phases Complete ✅**

The MIRA trading agent has been successfully expanded from a Python-centric Solana memecoin trader to a distributed, multi-language, multi-asset trading system supporting:

- 10 Programming Languages (Python, TypeScript, Rust, Go, C++, Julia, R, Java, SQL, Pine Script, MQL5)
- 9 Microservices with gRPC/HTTP/WebSocket APIs
- Demo and Live trading modes with broker-style account management
- Web dashboard for monitoring
- Comprehensive documentation
- Production-ready deployment configuration

### Quick Start Demo Mode

```bash
# 1. Clone repository
git clone https://github.com/Alitiora-Initiative/MIRA.git
cd MIRA

# 2. Start infrastructure
docker-compose up -d

# 3. Configure demo mode
cp trading-agent/config/config.example.yaml trading-agent/config/config.yaml
# Edit config.yaml: set account_mode.mode: demo

# 4. Start services (in separate terminals)
cd wallet-service && npm install && npm start
cd mev-engine && cargo run --release
cd trading-agent/python-engine && python main.py
```

### Dashboard

View the dashboard at: https://mira-trading-agent.vercel.app

### GitHub Repository

https://github.com/Alitiora-Initiative/MIRA

## Acknowledgments

Built with love by the MIRA team
