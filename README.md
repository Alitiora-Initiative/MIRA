# MIRA

Public research desk for market prints and logistics. The live site reads public quotes on the server. It does not paper-trade, invent prices, hold keys, or send orders.

Live site: https://mira-trading-agent.vercel.app

## What the site does

- **Desk** shows live public prices and the tape.
- **Markets** shows a one-day path from `/api/series`.
- **Flow** shows coverage, breadth, volume share, day range, and path variation from `/api/desk`.
- **Checks** runs a dry run against those same routes.

Simulations are restricted. Order routing is off.

## Server routes

| Route | Role |
| --- | --- |
| `/api/desk` | Quote board plus logistics. Cached for 45 seconds. |
| `/api/series?id=solana` | One-day public path for an allow-listed id. |

If the quote feed fails, the route says so. It does not substitute a simulated price.

## Repository map

The repository also contains service code in Python, TypeScript, Rust, Go, C++, Julia, R, Java, SQL, Pine Script, and MQL5. Those services are not started by this website. See `ARCHITECTURE_BLUEPRINT.md` for the layout.

## Still needed

- Order-book depth and venue spreads are not on the public quote feed.
- Wrapped equities listed in the repository have no matching public print here.
- Path variation uses the included 7-day spark only.

## License

MIT. See `LICENSE`.
