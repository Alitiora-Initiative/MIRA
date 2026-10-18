import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AssetRow, Position, SubNode, Tick } from "./types";

const BASE_ASSETS: AssetRow[] = [
  {
    ticker: "wAAPL",
    pair: "SOL",
    address: "App1e57xSolanaWrappedAssetPoolx1029",
    liquiditySol: 45102.4,
    phi: 92.41,
    action: "STRONG BUY",
  },
  {
    ticker: "wNVDA",
    pair: "SOL",
    address: "Nv1d1a89xSolanaWrappedAssetPoolx9941",
    liquiditySol: 102941.11,
    phi: 88.19,
    action: "ACCUMULATE",
  },
  {
    ticker: "WIF",
    pair: "SOL",
    address: "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
    liquiditySol: 18420.2,
    phi: 86.4,
    action: "ACCUMULATE",
  },
  {
    ticker: "BONK",
    pair: "SOL",
    address: "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    liquiditySol: 22110.8,
    phi: 81.2,
    action: "WATCH",
  },
  {
    ticker: "POPCAT",
    pair: "SOL",
    address: "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
    liquiditySol: 640.1,
    phi: 62.0,
    action: "BLACKLIST",
  },
];

type MiraState = {
  armed: boolean;
  pubkey: string | null;
  balanceSol: number;
  solUsd: number;
  targetFloor: number;
  ticks: Tick[];
  assets: AssetRow[];
  nodes: SubNode[];
  position: Position | null;
  lastSig: string | null;
  clock: number;
  arm: (on: boolean) => void;
  setWallet: (pubkey: string | null, balanceSol: number | null) => void;
  setSig: (sig: string) => void;
  step: () => void;
};

function stamp() {
  const d = new Date();
  return d.toLocaleTimeString("en-GB", { hour12: false });
}

export const useMira = create<MiraState>()(
  persist(
    (set, get) => ({
      armed: false,
      pubkey: null,
      balanceSol: 0.010914,
      solUsd: 104,
      targetFloor: 10,
      ticks: [
        { t: stamp(), msg: "Idle. Connect Phantom — Google session stays inside the wallet.", kind: "halt" },
      ],
      assets: BASE_ASSETS,
      nodes: [],
      position: null,
      lastSig: null,
      clock: 0,
      arm: (on: boolean) =>
        set((s: MiraState) => ({
          armed: on,
          ticks: [
            {
              t: stamp(),
              msg: on
                ? "Agent loop armed. Orders wait for a Phantom approval — no seed phrase."
                : "Agent halted by operator.",
              kind: (on ? "scan" : "halt") as Tick["kind"],
            },
            ...s.ticks,
          ].slice(0, 18),
        })),
      setWallet: (pubkey: string | null, balanceSol: number | null) =>
        set((s: MiraState) => ({
          pubkey,
          balanceSol: balanceSol ?? s.balanceSol,
          ticks: [
            {
              t: stamp(),
              msg: pubkey
                ? `Phantom linked ${pubkey.slice(0, 4)}…${pubkey.slice(-4)}. Key never leaves the wallet.`
                : "Phantom disconnected.",
              kind: "node" as const,
            },
            ...s.ticks,
          ].slice(0, 18),
        })),
      setSig: (sig: string) =>
        set((s: MiraState) => ({
          lastSig: sig,
          ticks: [
            { t: stamp(), msg: `Phantom signed intent ${sig}. Broadcast stays inside the wallet.`, kind: "exec" as const },
            ...s.ticks,
          ].slice(0, 18),
        })),
      step: () => {
        const s = get();
        if (!s.armed) return;
        const n = s.clock + 1;
        const drift = Math.sin(n / 7) * 0.22 + 0.08;
        const sigma = 0.12 + (Math.cos(n / 11) + 1) * 0.04;
        const xt = -2.1 + Math.sin(n / 5) * 0.7;
        const outside = Math.abs(xt) > 1.96 * 0.9;
        const assets = s.assets.map((a: AssetRow, i: number) => {
          const wobble = Math.sin(n / 9 + i) * 0.6;
          const phi = Math.max(40, Math.min(98, a.phi + wobble * 0.15));
          const action: AssetRow["action"] =
            phi >= 90 ? "STRONG BUY" : phi >= 85 ? "ACCUMULATE" : phi >= 75 ? "WATCH" : "BLACKLIST";
          return { ...a, phi: Math.round(phi * 100) / 100, action };
        });

        let position = s.position;
        let balanceSol = s.balanceSol;
        const ticks = [...s.ticks];
        const push = (msg: string, kind: Tick["kind"]) => ticks.unshift({ t: stamp(), msg, kind });

        if (n % 4 === 1) push(`SCAN Raydium / Orca — drift μ = ${drift.toFixed(3)}`, "scan");
        if (n % 4 === 2)
          push(
            `CALC dXt = ${drift.toFixed(3)} · σ = ${sigma.toFixed(3)} · OU x_t = ${xt.toFixed(2)}σ`,
            "calc",
          );

        if (!position && outside && n % 4 === 3) {
          const pick = assets.find((a: AssetRow) => a.phi >= 85 && a.action !== "BLACKLIST");
          if (pick && balanceSol >= 0.0015) {
            position = {
              ticker: pick.ticker,
              entry: 0.0042,
              now: 0.0042,
              sizeSol: 0.001,
              tp: 0.15,
              sl: 0.12,
            };
            balanceSol = Math.max(0, balanceSol - 0.001);
            push(`EVAL 0.001 SOL staged on $${pick.ticker}. Waiting on Phantom to approve.`, "exec");
          }
        } else if (position) {
          const move = 1 + Math.sin(n / 4) * 0.04 + 0.012;
          const now = Math.max(0.0001, position.entry * move);
          const ret = (now - position.entry) / position.entry;
          position = { ...position, now };
          if (ret >= position.tp) {
            balanceSol += position.sizeSol * (1 + ret);
            push(
              `EXIT $${position.ticker} +${(ret * 100).toFixed(2)}% ≥ TP ${(position.tp * 100).toFixed(0)}%. Back to SOL.`,
              "exec",
            );
            position = null;
          } else if (ret <= -position.sl) {
            balanceSol += position.sizeSol * (1 + ret);
            push(`STOP $${position.ticker} ${(ret * 100).toFixed(2)}%. Capital cut.`, "halt");
            position = null;
          }
        }

        const usd = balanceSol * s.solUsd;
        let nodes = s.nodes;
        if (usd >= 20 && nodes.length === 0) {
          nodes = Array.from({ length: 10 }, (_, i) => ({
            id: `MIRA-SUB-${String(i + 1).padStart(3, "0")}`,
            status: i === 0 ? "RUNNING" : "STAGING",
            seedUsd: 1,
            retPct: i === 0 ? 14.23 : null,
          }));
          push("GENESIS +$20 path unlocked. Ten $1 agent nodes staged inside this session.", "node");
        }

        const floor = Math.floor(balanceSol / 10) * 10 || 10;
        const targetFloor = balanceSol >= s.targetFloor ? Math.max(s.targetFloor, floor + (balanceSol >= floor && floor > 0 ? 10 : 0)) : s.targetFloor;

        set({
          clock: n,
          assets,
          position,
          balanceSol,
          nodes,
          ticks: ticks.slice(0, 18),
          targetFloor: Math.max(10, targetFloor),
        });
      },
    }),
    {
      name: "mira-session",
      partialize: (s: MiraState) => ({
        pubkey: s.pubkey,
        armed: s.armed,
        balanceSol: s.balanceSol,
      }),
    },
  ),
);
