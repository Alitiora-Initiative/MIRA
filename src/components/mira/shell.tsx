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
    <div className="min-h-screen bg-bg text-fg">
      <header className="sticky top-0 z-20 border-b border-line bg-bg/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-3 px-4 py-3">
          <Link to="/" className="flex items-center gap-2 font-semibold tracking-wide">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-teal-dim text-teal">
              <Activity size={16} />
            </span>
            MIRA
          </Link>
          <nav className="flex gap-1 text-sm">
            <Tab href="/" active={path === "/"} label="Hub" />
            <Tab href="/dashboard" active={path.startsWith("/dashboard")} label="Analytics" />
          </nav>
          <div className="ml-auto flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-2 rounded-full border border-line px-3 py-1 text-xs text-muted">
              <Radio size={12} className={armed ? "live-dot text-teal" : "text-muted"} />
              {armed ? "AGENT LIVE" : "STANDBY"}
            </span>
            {pubkey ? (
              <button
                type="button"
                className="h-11 rounded-full border border-line bg-surface px-4 text-sm"
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
                className="h-11 rounded-full bg-teal px-4 text-sm font-semibold text-ink"
                onClick={() => void onConnect()}
              >
                {phantomInstalled() ? "Connect Phantom" : "Connect Phantom"}
              </button>
            )}
            <button
              type="button"
              className={`h-11 rounded-full px-4 text-sm font-semibold ${armed ? "bg-rose text-ink" : "border border-teal text-teal"}`}
              onClick={() => arm(!armed)}
            >
              {armed ? "Halt agent" : "Arm agent"}
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
    </div>
  );
}

function Tab({ href, label, active }: { href: "/" | "/dashboard"; label: string; active: boolean }) {
  return (
    <Link
      to={href}
      className={`rounded-full px-3 py-2 text-sm ${active ? "bg-surface-2 text-fg" : "text-muted"}`}
    >
      {label}
    </Link>
  );
}
