# MIRA - Mathematical Intelligence for Recursive Asset-allocation

Autonomous, private AI trading agent for Solana ecosystem. Operates under continuous-time calculus models, multi-variate stochastic calculus equations, and real-time market liquidity metrics with absolute logical independence.

## System Architecture

### Base Operational Systems
- Initial Minimum Seed Capitalization: $0.60 USD equivalent in Native Solana (SOL)
- Active Operational Allocation Unit: 0.001 SOL minimum, 10 SOL maximum per order
- Lifespan Capabilities: Daemonized runtime engine for 4-hour bursts, scaling to 244 hours with error-handling loops
- Target Assets: Solana Memecoins, wrapped liquidity pool tokens, Tokenized Stocks
- Data Aggregation: DexScreener Developer APIs, Birdeye APIs, Helius RPC streams
- Transaction Execution: Jupiter Aggregator V6 API with Jito Block Engine (MEV Bundles) with priority validator tip

### Unified Asset Rating System (Φ Matrix)

Formula: Φ = ω1 · Ld + ω2 · (1 - H) + ω3 · Vv

Weights:
- ω1 = 0.50 (Liquidity Density)
- ω2 = 0.30 (Holders Concentration)
- ω3 = 0.20 (Volumetric Velocity Vector)

Components:
- Liquidity Density (Ld): min(1.0, Pool_TVL / $10,000 USD Baseline)
- Holder Concentration Skew (H): Normalized Herfindahl-Hirschman Index across top 10 token supply tracking vectors
- Volumetric Velocity Vector (Vv): tanh(ΔVolume_15m / Average_Volume_24h)

Gatekeeping Gateways:
- Immediate programmatic contract blacklisting unless Mint Authority == Revoked AND Burned_LP_Tokens == 100%
- Minimum Φ score: ≥ 85.0% for capital exposure

### Continuous Risk Parameters & Bracket Management
- Real-Time Price Tracking Matrix (Pt) against Initial Position Entry Cost Basis (P0)
- Take-Profit Trigger Floor: +10.0%
- Take-Profit Cap: +1000.0%
- Stop-Loss Capitulation Floor: -10.0%
- Stop-Loss Ceiling Guardrail: -40.0%
- Closing Execution Loop: Immediate cross-swap when Pt matches risk boundary

### Recursive Scaling & Dual-Stage Perpetual Matrix
- Step-Wise UI Milestone Targets: 10 SOL → 20 SOL → 30 SOL (incremental loop)
- Sub-Agent Horizontal Genesis Milestone: At +$20.00 USD profit, trigger capital-splitting routine
  - Reserve $10.00 USD in core pool
  - Provision 10 sub-agents in isolated Docker micro-containers (Alpine, 128MB RAM, 0.25 CPU)
  - Seed each container with exactly $1.00 USD isolated trading capital
- Perpetual Scaling Engine: At ≥ $200.00 USD valuation, scale to cross-margin derivatives
  - Open leverage-shielded perpetual long/short positions on Drift or Mango Markets
  - Execute at 00:00 and 12:00 UTC schedule updates
  - Use instantaneous directional drift calculation as execution signal vector

### System Integrity & Private Key Override Protection
- Non-Custodial Multi-Party Computation (MPC) Threshold (2, 3) Split Scheme
- Transaction validation requires partial signature from sandboxed local client (Share S1) + biometrically authorized cloud routing infrastructure token (Share S2)
- Single plaintext raw private key text string DOES NOT EXIST in codebase

## Architecture

```
trading-agent/
├── python-engine/
│   ├── core/
│   │   ├── config.py                     # Configuration dataclasses
│   │   ├── engine.py                     # Main orchestrator
│   │   └── real_trading_engine.py        # Live trading implementation
│   ├── strategies/
│   │   ├── math_strategies.py            # Calculus & probability strategies
│   │   └── strategy_manager.py           # Strategy orchestration
│   ├── exchanges/
│   │   └── exchange_manager.py           # Exchange API connections
│   ├── solana/
│   │   ├── phi_matrix.py                 # Φ Matrix asset rating system
│   │   ├── jupiter_router.py             # Jupiter Aggregator V6 integration
│   │   ├── jito_bundle.py                # Jito Block Engine MEV protection
│   │   ├── mpc_signer.py                 # MPC threshold signature scheme
│   │   └── helius_client.py              # Helius RPC data aggregation
│   ├── risk/
│   │   └── risk_manager.py               # Continuous-time calculus risk management
│   ├── scaling/
│   │   ├── recursive_scaling.py          # Recursive scaling engine
│   │   └── subagent_genesis.py           # Sub-agent horizontal genesis
│   └── main.py                           # Entry point
├── subagents/
│   ├── subagent_manager.py               # Subagent orchestration
│   ├── subagent.py                       # Autonomous subagent
│   └── Dockerfile                        # Docker container (Alpine, 128MB RAM, 0.25 CPU)
├── config/
│   └── config.example.yaml               # Configuration template
└── docs/
    └── DEPLOYMENT.md                     # Deployment guide
```

## Installation

```bash
# From trading-agent/
cd python-engine
pip install -r requirements.txt

# Paper trading. No keys, no live orders.
# Omit MIRA_PAPER_CYCLES to keep the session running.
MIRA_PAPER_CYCLES=12 MIRA_PAPER_SLEEP=0 python main.py
```

The launcher loads `config/config.paper.yaml` when `config.yaml` is missing. Clips are hard-limited to **0.001–10 SOL**. Live signing, Jito submission, and webhook alerts without `MIRA_WEBHOOK_KEY` stay off.

```bash
# Optional local overrides
cp ../config/config.paper.yaml ../config/config.yaml
```

## Configuration

Edit `config/config.yaml` with Solana-specific parameters:

```yaml
solana:
  rpc_endpoint: YOUR_HELIUS_RPC_ENDPOINT
  commitment: confirmed
  jito_endpoint: YOUR_JITO_BLOCK_ENGINE_ENDPOINT
  jito_tip_lamports: 1000

trading:
  sol:
    min_trade: 0.001
    max_trade: 10.0
    min_deposit: 0.60

phi_matrix:
  liquidity_density_weight: 0.50
  holder_concentration_weight: 0.30
  volumetric_velocity_weight: 0.20
  minimum_phi_score: 85.0

risk_management:
  take_profit_floor: 0.10
  take_profit_cap: 10.0
  stop_loss_floor: -0.10
  stop_loss_ceiling: -0.40

mpc:
  threshold: 2
  total_shares: 3
  local_share_path: /path/to/local/share
  cloud_endpoint: YOUR_MPC_CLOUD_ENDPOINT
```

## Running the System

```bash
# Start the Python trading engine
cd python-engine
python main.py
```

## Deployment

### Docker (Full System)

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d
```

## License

MIT License
