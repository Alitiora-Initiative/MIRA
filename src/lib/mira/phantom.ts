export const KNOWN_VAULT = "EDZjEbRAtqyC8z6ta6PYHX161Xynt13tWpd7orKERkbz";
const RPC = "https://api.mainnet-beta.solana.com";

type PhantomProvider = {
  isPhantom?: boolean;
  publicKey?: { toString(): string } | null;
  connect: (opts?: { onlyIfTrusted?: boolean }) => Promise<{ publicKey: { toString(): string } }>;
  disconnect: () => Promise<void>;
  signMessage: (
    message: Uint8Array,
    display?: "utf8" | "hex",
  ) => Promise<{ signature: Uint8Array }>;
};

function getProvider(): PhantomProvider | null {
  if (typeof window === "undefined") return null;
  const w = window as Window & {
    phantom?: { solana?: PhantomProvider };
    solana?: PhantomProvider;
  };
  return w.phantom?.solana ?? (w.solana?.isPhantom ? w.solana : null);
}

export function phantomInstalled() {
  return Boolean(getProvider());
}

export async function connectPhantom(): Promise<string> {
  const p = getProvider();
  if (!p) throw new Error("NO_PHANTOM");
  const res = await p.connect();
  return res.publicKey.toString();
}

export async function disconnectPhantom() {
  const p = getProvider();
  if (p) await p.disconnect().catch(() => undefined);
}

export async function approveIntent(text: string): Promise<string> {
  const p = getProvider();
  if (!p) throw new Error("NO_PHANTOM");
  const bytes = new TextEncoder().encode(text);
  const { signature } = await p.signMessage(bytes, "utf8");
  return [...signature].slice(0, 8).map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function fetchSolBalance(pubkey: string): Promise<number | null> {
  try {
    const res = await fetch(RPC, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "getBalance",
        params: [pubkey],
      }),
    });
    if (!res.ok) return null;
    const json = (await res.json()) as { result?: { value?: number } };
    const lamports = json.result?.value;
    if (typeof lamports !== "number") return null;
    return lamports / 1_000_000_000;
  } catch {
    return null;
  }
}

export function shortKey(k: string) {
  if (k.length < 10) return k;
  return `${k.slice(0, 4)}…${k.slice(-4)}`;
}
