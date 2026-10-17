export type Tick = {
  t: string;
  msg: string;
  kind: "scan" | "calc" | "exec" | "halt" | "node";
};

export type AssetRow = {
  ticker: string;
  pair: string;
  address: string;
  liquiditySol: number;
  phi: number;
  action: "STRONG BUY" | "ACCUMULATE" | "WATCH" | "BLACKLIST";
};

export type SubNode = {
  id: string;
  status: "RUNNING" | "STAGING";
  seedUsd: number;
  retPct: number | null;
};

export type Position = {
  ticker: string;
  entry: number;
  now: number;
  sizeSol: number;
  tp: number;
  sl: number;
};
