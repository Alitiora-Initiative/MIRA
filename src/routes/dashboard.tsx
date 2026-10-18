import { createFileRoute } from "@tanstack/react-router";
import { Shell } from "@/components/mira/shell";
import { KNOWN_VAULT, shortKey } from "@/lib/mira/phantom";
import { useMira } from "@/lib/mira/store";

export const Route = createFileRoute("/dashboard")({ component: Dashboard });

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
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted">MIRA // Analytics</p>
          <h1 className="text-2xl font-semibold">Recursive capital desk</h1>
        </div>
        <span className="rounded-full border border-teal/40 px-3 py-1 font-mono text-xs text-teal">
          {armed ? "SYSTEM OK" : "HALTED"}
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <article className="rounded-2xl border border-line bg-surface p-4">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted">Initial floor</p>
          <p className="mt-2 text-3xl font-semibold">${usd.toFixed(2)}</p>
          <p className="font-mono text-xs text-muted">{balanceSol.toFixed(6)} SOL · min seed $0.60</p>
          <p className="mt-3 truncate font-mono text-xs text-teal">
            Base wallet {pubkey ? shortKey(pubkey) : `${shortKey(KNOWN_VAULT)} (not linked)`}
          </p>
          <p className="mt-1 text-xs text-muted">MPC split stays inside Phantom. This page never stores a key.</p>
        </article>
        <article className="rounded-2xl border border-line bg-surface p-4">
          <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-wider text-muted">
            <span>
              Progress · step {prev} → {next} SOL
            </span>
            <span className="text-amber">{pct.toFixed(1)}%</span>
          </div>
          <div className="mt-4 h-3 overflow-hidden rounded-full bg-surface-2">
            <div className="h-full rounded-full bg-teal" style={{ width: `${pct}%` }} />
          </div>
          <p className="mt-3 font-mono text-xs text-muted">
            {balanceSol.toFixed(2)} / {next.toFixed(2)} SOL · P = (B − Tₙ) / (Tₙ₊₁ − Tₙ)
          </p>
        </article>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_1.1fr]">
        <article className="rounded-2xl border border-line bg-surface">
          <div className="grid grid-cols-2 border-b border-line px-4 py-2 font-mono text-[11px] uppercase text-muted">
            <span>Parameter</span>
            <span>Value</span>
          </div>
          {[
            ["Active trade size", "0.001 SOL"],
            ["Take-profit band", "+10% → +1000%"],
            ["Stop-loss band", "−10% → −40%"],
            ["Open position", position ? `$${position.ticker}` : "none"],
            ["Entry Φ gate", "≥ 85%"],
            ["Signing", "Phantom approval"],
          ].map(([k, v]) => (
            <div key={k} className="grid grid-cols-2 border-b border-line px-4 py-3 text-sm last:border-0">
              <span className="text-muted">{k}</span>
              <span className="font-mono">{v}</span>
            </div>
          ))}
        </article>
        <article className="rounded-2xl border border-line bg-surface p-4">
          <p className="font-mono text-[11px] uppercase tracking-wider text-muted">Execution telemetry</p>
          <ul className="mt-3 space-y-2">
            {ticks.map((tick, i) => (
              <li key={`${tick.t}-${i}`} className="font-mono text-xs leading-relaxed text-fg/90">
                <span className="text-muted">[{tick.t}]</span> {tick.msg}
              </li>
            ))}
          </ul>
        </article>
      </div>

      <article className="mt-4 overflow-hidden rounded-2xl border border-line">
        <p className="bg-surface-2 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-muted">
          Sub-agent nodes · spawn after +$20 net
        </p>
        {nodes.length === 0 ? (
          <p className="px-4 py-6 text-sm text-muted">
            None yet. The master loop keeps trading 0.001 SOL clips until the session marks +$20, then stages ten
            $1 nodes. They live in this browser session — not a server you have to install.
          </p>
        ) : (
          nodes.map((n) => (
            <div
              key={n.id}
              className="grid grid-cols-2 gap-2 border-t border-line px-4 py-3 text-sm sm:grid-cols-4"
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
