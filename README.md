# MIRA

Autonomous Solana desk for a **Google-created Phantom wallet**.

Phantom holds the key. This app never asks for a seed phrase or a private key.

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
