# MIRA Roadmap — Multi-Language Architectural Blueprint

Human-maintained checklist. Deployments require a deliberate Git push (and Vercel rebuild).

## Current position

| Phase | Status |
| ----- | ------ |
| **Phase 1** Wallet & Web3 Execution (TypeScript + Rust) | **In progress** — TypeScript Phantom UI shipped; Rust MEV engine not started |
| Phase 2 Data Ingestion (Go + C++) | Not started |
| Phase 3 Analytics (Julia + R) | Not started |
| Phase 4 Backtesting & Broker (Java) | Not started |
| Phase 5 External Bridges (SQL + Pine + MQL) | Not started |

## Phase 1 objectives (active)

- [x] TypeScript wallet UI (Hub + Analytics)
- [x] Phantom connect / disconnect / signMessage (no seed phrase)
- [x] Session agent loop (Φ gate, 0.001 SOL clips, TP/SL bands, sub-agent genesis after +$20)
- [x] Deployable Vite app (Vercel project **JOJO**)
- [ ] TypeScript wallet-service (gRPC signer, WebSocket gateway)
- [ ] Rust MEV protection engine (sandwich detector, Jito private mempool, circuit breaker)
- [ ] gRPC protobuf (`wallet.proto`, `mev.proto`)
- [ ] Python gRPC client for wallet / MEV
- [ ] Config updates + integration tests

## Phase 2–5 (summary)

See the full multi-language blueprint in repo history / design docs:

- **Phase 2:** Go indexer + normalizer + mempool; C++ HFE for CEX perps; Kafka bus
- **Phase 3:** Julia portfolio optimizer + risk simulation; R GARCH / cointegration / LP analytics
- **Phase 4:** Java tick-level backtester + Interactive Brokers gateway
- **Phase 5:** PostgreSQL schema, TradingView Pine webhooks, MetaTrader MQL bridges

## Security rules (all phases)

- Private keys never leave the wallet / HSM
- No plain-text key storage
- User approval required for every staged order (Phantom signMessage path today)

## Explicitly out of scope until funded

- Mainnet capital with real value without independent audit
- Unauthenticated webhook ingestion
- Fabricated market charts presented as live data
