import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { ShieldCheck, Zap, TrendingUp } from "lucide-react";
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
    const note = `MIRA intent ${new Date().toISOString()} size=0.001 SOL wallet=${pubkey ?? "unlinked"}`;
    try {
      const sig = await approveIntent(note);
      setSig(sig);
    } catch {
      setSig("phantom-not-open");
    }
  }

  return (
    <Shell>
      <section className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-teal/30 bg-teal-dim/20 px-3 py-1 mb-4">
            <Zap size={14} className="text-teal" />
            <span className="font-mono text-xs text-teal">AI-POWERED TRADING</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-fg via-teal to-teal-light bg-clip-text text-transparent">
            Google Phantom. No seed phrase.
          </h1>
          <p className="mt-4 text-base leading-relaxed text-muted">
            You made this wallet with Google inside Phantom. Phantom keeps the key. MIRA only reads the public
            address and asks Phantom to approve each 0.001 SOL order.
          </p>
        </div>
        <div className="flex items-center gap-3 rounded-2xl border border-teal/30 bg-teal-dim/20 backdrop-blur-sm px-6 py-4">
          <TrendingUp className="text-teal" size={24} />
          <div>
            <p className="font-mono text-xs text-muted">Active contracts</p>
            <p className="text-2xl font-bold text-teal">{active}</p>
          </div>
        </div>
      </section>

      {!hasPhantom && (
        <div className="mb-6 rounded-2xl border border-amber/40 bg-amber/10 backdrop-blur-sm px-4 py-3 text-sm text-amber">
          Phantom is not in this browser yet. Open this page inside the Phantom app browser (the same Google
          account you used to create the wallet). Connect, then tap Approve.
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
        <aside className="rounded-2xl border border-line/50 bg-surface/80 backdrop-blur-sm p-4 shadow-glass">
          <p className="px-2 pb-3 font-mono text-[11px] uppercase tracking-wider text-muted">Tickers</p>
          <ul className="space-y-2">
            {PAIRS.map((p, i) => (
              <li
                key={p}
                className={`rounded-xl px-3 py-2.5 font-mono text-sm transition-all duration-300 ${i === 0 ? "bg-gradient-to-r from-teal-dim/50 to-teal-dim/30 text-teal border border-teal/30 shadow-glow" : "text-fg hover:bg-surface-2/50"}`}
              >
                ${p.split("-")[0]}
                <span className="text-muted">-{p.split("-")[1]}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 px-2 text-xs text-muted">Filter · rating above 85%</p>
        </aside>
        <div className="rounded-2xl border border-line/50 bg-surface/80 backdrop-blur-sm p-5 shadow-glass">
          <div className="mb-3 flex items-center justify-between">
            <p className="font-mono text-xs uppercase tracking-wider text-muted">SOL path · calculus domain</p>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-teal-dim/30 px-2.5 py-1 font-mono text-xs text-teal">
              <span className="w-1.5 h-1.5 rounded-full bg-teal live-dot"></span>
              no emotion weight
            </span>
          </div>
          <PriceChart seed={clock} />
        </div>
      </div>

      <div className="mt-6 overflow-hidden rounded-2xl border border-line/50 bg-surface/80 backdrop-blur-sm shadow-glass">
        <div className="grid grid-cols-[1fr_1.4fr_0.8fr_0.9fr] gap-2 bg-surface-2/50 px-4 py-3 font-mono text-[11px] uppercase tracking-wider text-muted border-b border-line/50">
          <span>Asset</span>
          <span className="hidden sm:block">Contract</span>
          <span>Liquidity</span>
          <span>Φ rating</span>
        </div>
        {assets.map((a) => (
          <div
            key={a.ticker}
            className="grid grid-cols-2 gap-2 border-t border-line/50 px-4 py-4 text-sm sm:grid-cols-[1fr_1.4fr_0.8fr_0.9fr] hover:bg-surface-2/30 transition-colors duration-200"
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

      <div className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-line/50 bg-surface/80 backdrop-blur-sm p-5 shadow-glass">
        <div className="flex items-start gap-4">
          <div className="rounded-xl bg-teal-dim/30 p-3">
            <ShieldCheck className="text-teal" size={20} />
          </div>
          <div>
            <p className="text-sm font-medium">Next order needs your thumb, not a private key.</p>
            <p className="text-xs text-muted mt-1">
              {position
                ? `Staged $${position.ticker} · 0.001 SOL · TP +${(position.tp * 100).toFixed(0)}% / SL −${(position.sl * 100).toFixed(0)}%`
                : "Arm the agent on Analytics. When a setup clears Φ ≥ 85 and the OU band, approve it here."}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => void approve()}
          className="h-12 rounded-full bg-gradient-to-r from-teal to-teal-light px-6 text-sm font-semibold text-ink shadow-glow hover:shadow-glow-strong transition-all duration-300"
        >
          Approve in Phantom
        </button>
      </div>
    </Shell>
  );
}
