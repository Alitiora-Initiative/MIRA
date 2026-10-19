import { createFileRoute } from "@tanstack/react-router";
import { Shell } from "@/components/mira/shell";
import { KNOWN_VAULT, shortKey } from "@/lib/mira/phantom";
import { useMira } from "@/lib/mira/store";
import { Activity, Cpu, BarChart3, Zap } from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  component: Dashboard,
});

function Dashboard() {
  const balanceSol = useMira((s) => s.balanceSol);
  const solUsd = useMira((s) => s.solUsd);
  const targetFloor = useMira((s) => s.targetFloor);
  const ticks = useMira((s) => s.ticks);
  const nodes = useMira((s) => s.nodes);
  const pubkey = useMira((s) => s.pubkey);
  const position = useMira((s) => s.position);
  const armed = useMira((s) => s.armed);

  const next = targetFloor;
  const prev = Math.max(0, next - 10);
  const span = next - prev || 10;
  const pct = Math.max(0, Math.min(100, ((balanceSol - prev) / span) * 100));
  const usd = balanceSol * solUsd;

  return (
    <Shell>
      <div className="mb-6 flex items-center justify-between fade-in">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-teal/30 bg-teal-dim/20 px-3 py-1 mb-3 shimmer-effect">
            <BarChart3 size={14} className="text-teal" />
            <span className="font-mono text-xs text-teal">ANALYTICS</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Recursive capital desk</h1>
        </div>
        <span className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 font-mono text-xs backdrop-blur-sm transition-all duration-300 ${armed ? "border-teal/40 bg-teal-dim/30 text-teal shadow-glow" : "border-line/50 bg-surface-2/30 text-muted"}`}>
          <span className={`w-2 h-2 rounded-full ${armed ? "bg-teal live-dot" : "bg-muted"}`}></span>
          {armed ? "SYSTEM OK" : "HALTED"}
        </span>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <article className="rounded-2xl border border-line/50 bg-surface/80 backdrop-blur-sm p-5 shadow-glass hover:shadow-glow transition-all duration-300 cinematic-border">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="text-teal" size={18} />
            <p className="font-mono text-[11px] uppercase tracking-wider text-muted">Initial floor</p>
          </div>
          <p className="mt-2 text-4xl font-bold bg-gradient-to-r from-fg to-teal bg-clip-text text-transparent">${usd.toFixed(2)}</p>
          <p className="font-mono text-xs text-muted mt-2">{balanceSol.toFixed(6)} SOL · min seed $0.60</p>
          <p className="mt-4 truncate font-mono text-xs text-teal">
            Base wallet {pubkey ? shortKey(pubkey) : `${shortKey(KNOWN_VAULT)} (not linked)`}
          </p>
          <p className="mt-1 text-xs text-muted">MPC split stays inside Phantom. This page never stores a key.</p>
        </article>
        <article className="rounded-2xl border border-line/50 bg-surface/80 backdrop-blur-sm p-5 shadow-glass hover:shadow-glow transition-all duration-300 cinematic-border">
          <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-wider text-muted mb-3">
            <span>Progress · step {prev} → {next} SOL</span>
            <span className="text-amber">{pct.toFixed(1)}%</span>
          </div>
          <div className="mt-4 h-4 overflow-hidden rounded-full bg-surface-2/50">
            <div className="h-full rounded-full bg-gradient-to-r from-teal to-teal-light shadow-glow transition-all duration-500" style={{ width: `${pct}%` }} />
          </div>
          <p className="mt-3 font-mono text-xs text-muted">
            {balanceSol.toFixed(2)} / {next.toFixed(2)} SOL · P = (B − Tₙ) / (Tₙ₊₁ − Tₙ)
          </p>
        </article>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_1.1fr]">
        <article className="rounded-2xl border border-line/50 bg-surface/80 backdrop-blur-sm shadow-glass cinematic-border">
          <div className="grid grid-cols-2 border-b border-line/50 px-4 py-3 font-mono text-[11px] uppercase text-muted bg-surface-2/30">
            <span>Parameter</span>
            <span>Value</span>
          </div>
          {[
            ["SOL clip", "0.001 – 10"],
            ["Mode", "paper"],
            ["Take-profit band", "+10% → +1000%"],
            ["Stop-loss band", "−10% → −40%"],
            ["Open position", position ? `$${position.ticker}` : "none"],
            ["Entry Φ gate", "≥ 85%"],
            ["Signing", "Phantom approval"],
          ].map(([k, v]) => (
            <div key={k} className="grid grid-cols-2 border-b border-line/50 px-4 py-3 text-sm last:border-0 hover:bg-surface-2/20 transition-colors duration-200">
              <span className="text-muted">{k}</span>
              <span className="font-mono">{v}</span>
            </div>
          ))}
        </article>
        <article className="rounded-2xl border border-line/50 bg-surface/80 backdrop-blur-sm p-5 shadow-glass cinematic-border">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="text-teal" size={18} />
            <p className="font-mono text-[11px] uppercase tracking-wider text-muted">Execution telemetry</p>
          </div>
          <ul className="mt-3 space-y-2 max-h-64 overflow-y-auto">
            {ticks.map((tick, i) => (
              <li key={`${tick.t}-${i}`} className="font-mono text-xs leading-relaxed text-fg/90 px-3 py-2 rounded-lg hover:bg-surface-2/30 transition-colors duration-200">
                <span className="text-muted">[{tick.t}]</span> {tick.msg}
              </li>
            ))}
          </ul>
        </article>
      </div>

      <article className="mt-6 overflow-hidden rounded-2xl border border-line/50 bg-surface/80 backdrop-blur-sm shadow-glass cinematic-border">
        <div className="flex items-center gap-2 bg-surface-2/30 px-4 py-3 font-mono text-[11px] uppercase tracking-wider text-muted border-b border-line/50">
          <Cpu className="text-teal" size={16} />
          <span>Sub-agent nodes · spawn after +$20 net</span>
        </div>
        {nodes.length === 0 ? (
          <p className="px-4 py-6 text-sm text-muted">
            None yet. Paper clips stay inside 0.001–10 SOL. Ten $1 nodes stage only after the session marks +$20.
          </p>
        ) : (
          nodes.map((n) => (
            <div
              key={n.id}
              className="grid grid-cols-2 gap-2 border-t border-line/50 px-4 py-4 text-sm sm:grid-cols-4 hover:bg-surface-2/20 transition-colors duration-200"
            >
              <span className="font-mono">{n.id}</span>
              <span className={n.status === "RUNNING" ? "text-teal" : "text-amber"}>{n.status}</span>
              <span>${n.seedUsd.toFixed(2)} seed</span>
              <span>{n.retPct == null ? "awaiting swap" : `+${n.retPct.toFixed(2)}%`}</span>
            </div>
          ))
        )}
      </article>
    </Shell>
  );
}
