# MIRA Core — Production Autonomous On-Chain Trading Engine

**Production-Grade Autonomous On-Chain Trading Engine with Native Jupiter V6 API Connection Routing**

This repository contains the live, operational infrastructure for Mira. All mock logic, data simulations, and placeholders have been removed. The system communicates directly with the **Solana Mainnet** JSON-RPC network and the **Jupiter Aggregator V6** API.

It features:
- Automatic transaction generation
- Base64 raw buffer deserialization
- Cryptographic message signing (solders)
- Live transaction broadcasts using standard Versioned Transactions
- Recursive sub-agent mitosis engine
- React 19 telemetry dashboard

---

## Architecture Overview

```
[Live JSON-RPC / Solana Mainnet Cluster Node]
          ▲                    │
(Broadcast raw signed binary)  │  (Account balance data tracking)
          │                    ▼
┌───────────────────────────────────────────────┐
│           MIRA CORE AGENT ENGINE              │ ◄─── [React 19 Telemetry Dashboard]
└───────────────────────┬───────────────────────┘
                        │
        (Get Quote payload) │ (Post Signed Transaction Payload Buffer)
                        ▼                    ▲
┌───────────────────────────────────────────────┐
│     JUPITER AGGREGATOR V6 SWAP API ROUTER     │
│     Endpoints: /swap/v1/quote & /swap/v1/swap │
└───────────────────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐   (Triggered exactly at $20.00 USD)
          ▼                           ▼
   [Sub-Agent 01]              [Sub-Agent 15]  ──► Milestones: Tier 1 ($20)
   Allocation: $1.00           Allocation: $1.00       Tier 2 ($100)
                                                       Tier 3 ($1000)
```

---

## Core Components

### 1. Telemetry Interface (`src/Dashboard.tsx`)
Production-grade React dashboard tracking:
- Core vault SOL / USD balance
- Progress toward 10 SOL goal
- 4-hour autonomous engine timeout window
- Live on-chain transaction ledger
- Recursive sub-agent fleet matrix (mitosis)

### 2. Live Execution Engine (`mira_jup_router.py`)
- Asynchronous Solana JSON-RPC client (Mainnet)
- Jupiter V6 quote + swap endpoints
- VersionedTransaction deserialization from base64
- Cryptographic signing with `solders`
- `send_raw_transaction` broadcast
- Dynamic compute unit limit + 50,000 lamport priority fee
- Hard safety floor ($0.60 USD)
- Automatic mitosis trigger at $20.00 USD core balance

### 3. System Constraints & Mitosis Logic
When the parent wallet balance reaches **$20.00 USD**:
1. Parent trading lines are halted
2. Remaining capital is partitioned into **15 sub-agents** ($1.00 USD each)
3. Exactly **$5.00 USD** is left in the parent wallet for gas reserves
4. Sub-agents inherit the same Jupiter routing engine under independent keypaths

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for dashboard)
- Solana Mainnet RPC endpoint (Helius, QuickNode, or public)
- Funded Solana keypair (never commit private keys)

### 1. Clone & Environment
```bash
git clone https://github.com/Alitiora-Initiative/MIRA.git
cd MIRA
cp .env.example .env
# Edit .env with your RPC URL and private key
```

### 2. Python Engine
```bash
pip install -r requirements.txt
python mira_jup_router.py
```

### 3. React Dashboard
```bash
cd src
npm install
npm run dev
```

---

## Safety Notes

- This system executes **real Mainnet transactions**.
- Always start with minimal capital.
- Private keys must never be committed to the repository.
- The $0.60 USD floor and mitosis logic are hard-coded safety guards.
- Priority fees are set to 50,000 lamports by default; adjust according to network conditions.

---

## License

MIT — Alitiora Initiative
