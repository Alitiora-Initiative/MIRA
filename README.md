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

### 🚧 Phase 3: Enhanced Analytics Layer (PENDING)

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

- [x] Phase 1: Wallet & Web3 Execution Layer
- [ ] Phase 2: Data Ingestion Pipeline (Go + C++)
- [ ] Phase 3: Enhanced Analytics Layer (Julia + R)
- [ ] Phase 4: Enterprise Backtesting (Java)
- [ ] Phase 5: External Bridges (SQL + Pine Script + MQL4/MQL5)
- [ ] Production Deployment & Optimization

## Acknowledgments

Built with love by the MIRA team
