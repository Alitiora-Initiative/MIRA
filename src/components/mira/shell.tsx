import { Link, useRouterState } from "@tanstack/react-router";
import { Activity, Radio } from "lucide-react";
import { useEffect } from "react";
import { connectPhantom, disconnectPhantom, fetchSolBalance, phantomInstalled, shortKey } from "@/lib/mira/phantom";
import { useMira } from "@/lib/mira/store";

export function Shell({ children }: { children: React.ReactNode }) {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const armed = useMira((s) => s.armed);
  const pubkey = useMira((s) => s.pubkey);
  const arm = useMira((s) => s.arm);
  const setWallet = useMira((s) => s.setWallet);
  const step = useMira((s) => s.step);

  useEffect(() => {
    if (!armed) return;
    const id = window.setInterval(() => step(), 1600);
    return () => window.clearInterval(id);
  }, [armed, step]);

  async function onConnect() {
    try {
      const key = await connectPhantom();
      const bal = await fetchSolBalance(key);
      setWallet(key, bal);
    } catch {
      setWallet(null, null);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0d1117] via-[#07090f] to-[#05070a] text-fg">
      <header className="sticky top-0 z-20 border-b border-line/50 glass">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-3 px-4 py-3">
          <Link to="/" className="flex items-center gap-2 font-semibold tracking-wide group">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-teal-dim to-teal text-teal-light shadow-glow group-hover:shadow-glow-strong transition-all duration-300">
              <Activity size={18} />
            </span>
            <span className="text-xl font-bold bg-gradient-to-r from-teal to-teal-light bg-clip-text text-transparent">
              MIRA
            </span>
          </Link>
          <nav className="flex gap-1 text-sm">
            <Tab href="/" active={path === "/"} label="Hub" />
            <Tab href="/dashboard" active={path.startsWith("/dashboard")} label="Analytics" />
          </nav>
          <div className="ml-auto flex flex-wrap items-center gap-2">
            <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs backdrop-blur-sm transition-all duration-300 ${armed ? "border-teal/40 bg-teal-dim/30 text-teal shadow-glow" : "border-line/50 bg-surface-2/30 text-muted"}`}>
              <Radio size={12} className={armed ? "live-dot text-teal" : "text-muted"} />
              {armed ? "AGENT LIVE" : "STANDBY"}
            </span>
            {pubkey ? (
              <button
                type="button"
                className="h-11 rounded-full border border-line/50 bg-surface/80 backdrop-blur-sm px-4 text-sm hover:border-teal/50 hover:bg-surface-2/80 transition-all duration-300"
                onClick={() => {
                  void disconnectPhantom();
                  setWallet(null, null);
                }}
              >
                {shortKey(pubkey)}
              </button>
            ) : (
              <button
                type="button"
                className="h-11 rounded-full bg-gradient-to-r from-teal to-teal-light px-4 text-sm font-semibold text-ink shadow-glow hover:shadow-glow-strong transition-all duration-300"
                onClick={() => void onConnect()}
              >
                {phantomInstalled() ? "Connect Phantom" : "Connect Phantom"}
              </button>
            )}
            <button
              type="button"
              className={`h-11 rounded-full px-4 text-sm font-semibold transition-all duration-300 ${armed ? "bg-gradient-to-r from-rose to-rose text-ink shadow-glow hover:shadow-glow-strong" : "border border-teal/50 text-teal hover:bg-teal-dim/20"}`}
              onClick={() => arm(!armed)}
            >
              {armed ? "Halt agent" : "Arm agent"}
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
    </div>
  );
}

function Tab({ href, label, active }: { href: "/" | "/dashboard"; label: string; active: boolean }) {
  return (
    <Link
      to={href}
      className={`rounded-full px-4 py-2 text-sm font-medium transition-all duration-300 ${active ? "bg-gradient-to-r from-teal-dim/50 to-teal-dim/30 text-teal border border-teal/30 shadow-glow" : "text-muted hover:text-fg hover:bg-surface-2/30"}`}
    >
      {label}
    </Link>
  );
}
