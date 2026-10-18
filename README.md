# MIRA

Autonomous Solana desk for a **Google-created Phantom wallet**.

Phantom holds the key. This app never asks for a seed phrase or a private key.

## Live

Deployed on Vercel as **JOJO** (see latest deployment URL after push).

## What you do

1. Open the live app in the **Phantom in-app browser** (same Google account that created the wallet).
2. Tap **Connect Phantom**.
3. Open **Analytics** and tap **Arm agent**.
4. When a 0.001 SOL setup is staged, tap **Approve in Phantom**. You confirm inside the wallet.

## Rules baked in

- Floor: about $0.60 in SOL
- Clip size: 0.001 SOL
- Take-profit band: +10% to +1000%
- Stop-loss band: -10% to -40%
- Asset gate: score Φ ≥ 85, mint authority revoked, LP burned
- After +$20, ten $1 sub-agent nodes are staged in the session
- Progress steps 10 → 20 → 30 SOL

Watched address until you connect: `EDZjEbRAtqyC8z6ta6PYHX161Xynt13tWpd7orKERkbz`

## Stack (Phase 1 — current)

- Vite + React 19 + TypeScript
- TanStack Router
- Zustand (session state)
- Tailwind CSS v4
- Recharts
- Phantom Wallet Standard (connect + signMessage)

## Roadmap

See [ROADMAP.md](./ROADMAP.md) for the multi-language architectural blueprint (Python core → TypeScript/Rust wallet → Go/C++ data → Julia/R analytics → Java backtesting → SQL/Pine/MQL bridges).

**Current position:** Phase 1 foundation — TypeScript wallet UI + Phantom signing path (no private keys).

## Develop

```bash
npm install
npm run dev
```

## Operator

Alitiora Initiative · Joseph Mushelle Nyingeh · Kenya
