import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { ShieldCheck } from "lucide-react";
import { PriceChart } from "@/components/mira/price-chart";
import { Shell } from "@/components/mira/shell";
import { approveIntent, phantomInstalled } from "@/lib/mira/phantom";
import { useMira } from "@/lib/mira/store";

export const Route = createFileRoute("/")({ component: Home });

const PAIRS = ["SOL-USD", "BONK-SOL", "WIF-SOL", "POPCAT-SOL", "wAAPL-SOL", "wNVDA-SOL"];

function Home() {
  const assets = useMira((s) => s.assets);
  const clock = useMira((s) => s.clock);
  const position = useMira((s) => s.position);
  const pubkey = useMira((s) => s.pubkey);
  const setSig = useMira((s) => s.setSig);
  const active = assets.filter((a) => a.action !== "BLACKLIST").length;
  const [hasPhantom, setHasPhantom] = useState(true);

  useEffect(() => {
    setHasPhantom(phantomInstalled());
  }, []);

  async function approve() {
    const size = position?.sizeSol ?? 0.001;
    const note = `MIRA paper intent ${new Date().toISOString()} size=${size} SOL wallet=${pubkey ?? "unlinked"}`;
    try {
      const sig = await approveIntent(note);
      setSig(sig);
    } catch {
      setSig("phantom-not-open");
    }
  }

  return (
    <Shell>
      <section className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted">MIRA // Global hub</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Google Phantom. No seed phrase.</h1>
          <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted">
            Paper book only. Phantom keeps the key. Each fill is clipped to 0.001–10 SOL and still needs your approval.
          </p>
        </div>
        <p className="font-mono text-xs text-amber">Active contracts {active}</p>
      </section>

      {!hasPhantom && (
        <div className="mb-5 rounded-2xl border border-amber/40 bg-surface px-4 py-3 text-sm text-amber">
          Phantom is not in this browser yet. Open this page inside the Phantom app browser (the same Google
          account you used to create the wallet). Connect, then tap Approve.
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-[220px_1fr]">
        <aside className="rounded-2xl border border-line bg-surface p-3">
          <p className="px-2 pb-2 font-mono text-[11px] uppercase tracking-wider text-muted">Tickers</p>
          <ul className="space-y-1">
            {PAIRS.map((p, i) => (
              <li
                key={p}
                className={`rounded-lg px-2 py-2 font-mono text-sm ${i === 0 ? "bg-teal-dim text-teal" : "text-fg"}`}
              >
                ${p.split("-")[0]}
                <span className="text-muted">-{p.split("-")[1]}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 px-2 text-xs text-muted">Filter · rating above 85%</p>
        </aside>
        <div className="rounded-2xl border border-line bg-surface p-4">
          <div className="mb-2 flex items-center justify-between">
            <p className="font-mono text-xs uppercase tracking-wider text-muted">SOL path · calculus domain</p>
            <p className="font-mono text-xs text-teal">no emotion weight</p>
          </div>
          <PriceChart seed={clock} />
        </div>
      </div>

      <div className="mt-4 overflow-hidden rounded-2xl border border-line">
        <div className="grid grid-cols-[1fr_1.4fr_0.8fr_0.9fr] gap-2 bg-surface-2 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-muted">
          <span>Asset</span>
          <span className="hidden sm:block">Contract</span>
          <span>Liquidity</span>
          <span>Φ rating</span>
        </div>
        {assets.map((a) => (
          <div
            key={a.ticker}
            className="grid grid-cols-2 gap-2 border-t border-line px-4 py-3 text-sm sm:grid-cols-[1fr_1.4fr_0.8fr_0.9fr]"
          >
            <span className="font-medium">${a.ticker}</span>
            <span className="hidden truncate font-mono text-xs text-muted sm:block">{a.address}</span>
            <span className="font-mono text-xs">{a.liquiditySol.toLocaleString()} SOL</span>
            <span className={a.phi >= 85 ? "text-teal" : a.action === "BLACKLIST" ? "text-rose" : "text-amber"}>
              {a.phi.toFixed(2)}% · {a.action}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-line bg-surface p-4">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-0.5 text-teal" size={18} />
          <div>
            <p className="text-sm font-medium">Next order needs your thumb, not a private key.</p>
            <p className="text-xs text-muted">
              {position
                ? `Paper $${position.ticker} · ${position.sizeSol} SOL · TP +${(position.tp * 100).toFixed(0)}% / SL −${(position.sl * 100).toFixed(0)}%`
                : "Arm the agent on Analytics. When a setup clears Φ ≥ 85 and the OU band, approve it here."}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => void approve()}
          className="h-11 rounded-full bg-teal px-5 text-sm font-semibold text-ink"
        >
          Approve in Phantom
        </button>
      </div>
    </Shell>
  );
}
