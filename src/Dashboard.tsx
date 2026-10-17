import React, { useState, useEffect, useMemo } from 'react';
import { Activity, Shield, Flame, GitFork, Cpu, Layers, TrendingUp, AlertTriangle } from 'lucide-react';

interface LiveTransaction {
  signature: string;
  symbol: string;
  amountSol: number;
  direction: 'BUY' | 'SELL';
  slot: number;
  timestamp: string;
}

interface SubAgent {
  id: string;
  pubkey: string;
  balanceUsd: number;
  currentMilestone: string;
  status: 'IDLE' | 'TRADING' | 'HALTED';
}

export default function MiraLiveDashboard() {
  const [solPrice] = useState<number>(145.20);
  const [coreSolBalance, setCoreSolBalance] = useState<number>(0.138);
  const [targetGoalSol] = useState<number>(10.0);
  const [isAutonomousActive, setIsAutonomousActive] = useState<boolean>(false);
  const [timeRemaining, setTimeRemaining] = useState<number>(14400);
  const [liveTransactions, setLiveTransactions] = useState<LiveTransaction[]>([]);
  const [subAgents, setSubAgents] = useState<SubAgent[]>([]);

  const coreUsdBalance = useMemo(
    () => coreSolBalance * solPrice,
    [coreSolBalance, solPrice]
  );

  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;
    if (isAutonomousActive) {
      interval = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            setIsAutonomousActive(false);
            return 14400;
          }
          return prev - 1;
        });

        // Trigger recursive mitosis when criteria are hit
        if (coreUsdBalance <= 20.0 && subAgents.length === 0) {
          const generatedAgents: SubAgent[] = Array.from({ length: 15 }).map((_, i) => ({
            id: `MIRA-SUB-${String(i + 1).padStart(2, '0')}`,
            pubkey: `SubAgentKeypairDerivationPathM44H501H${i}H0`,
            balanceUsd: 1.0,
            currentMilestone: 'Tier-1 ($20)',
            status: 'TRADING' as const,
          }));
          setSubAgents(generatedAgents);
          setCoreSolBalance(5.0 / solPrice);
        }
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isAutonomousActive, coreUsdBalance, subAgents.length, solPrice]);

  return (
    <div className="w-full min-h-screen bg-[#060814] text-[#cbd5e1] p-6 font-mono tracking-tight">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center border border-slate-800 bg-[#0a1128] p-6 rounded-xl mb-6 shadow-2xl gap-4">
        <div className="flex items-center gap-3">
          <div
            className={`p-2 rounded-lg ${
              isAutonomousActive ? 'bg-teal-500/10 text-teal-400' : 'bg-rose-500/10 text-rose-400'
            }`}
          >
            <Cpu
              className={`w-6 h-6 ${isAutonomousActive ? 'animate-spin' : ''}`}
              style={{ animationDuration: '8s' }}
            />
          </div>
          <div>
            <h1 className="text-xl font-black text-white tracking-widest flex items-center gap-2">
              MIRA NODE V1.0
            </h1>
            <p className="text-xs text-slate-400">Direct Production Node Connection Matrix</p>
          </div>
        </div>
        <button
          onClick={() => setIsAutonomousActive(!isAutonomousActive)}
          className={`px-6 py-3 rounded-lg text-xs font-black transition-all border ${
            isAutonomousActive
              ? 'bg-rose-500 text-white border-rose-400'
              : 'bg-gradient-to-r from-teal-500 to-emerald-500 text-slate-950 border-teal-300'
          }`}
        >
          {isAutonomousActive ? 'HALT INTERFACE RUNTIME' : 'ENGAGE 4HR ENGINE LOOP'}
        </button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-[#0a1128] p-6 rounded-xl border border-slate-800 shadow-xl">
          <span className="text-xs text-slate-400 font-bold block uppercase">
            CURRENT VAULT ACCOUNT SIZE
          </span>
          <h2 className="text-3xl font-black text-white mt-1">
            {coreSolBalance.toFixed(6)}{' '}
            <span className="text-xs text-teal-400 font-normal">SOL</span>
          </h2>
          <span className="text-xs text-slate-500 block mt-0.5">
            ≈ ${coreUsdBalance.toFixed(2)} USD
          </span>
        </div>

        <div className="bg-[#0a1128] p-6 rounded-xl border border-slate-800 shadow-xl">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-slate-400 font-bold uppercase">ROADMAP TO 10 SOL GOAL</span>
            <span className="text-xs font-bold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
              10 SOL TARGET
            </span>
          </div>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-black text-white">
              {((coreSolBalance / targetGoalSol) * 100).toFixed(2)}%
            </span>
          </div>
          <div className="w-full bg-slate-950 h-3 rounded-full mt-4 border border-slate-800 p-0.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-teal-400 to-purple-500 h-full rounded-full transition-all"
              style={{
                width: `${Math.min(100, (coreSolBalance / targetGoalSol) * 100)}%`,
              }}
            />
          </div>
        </div>

        <div className="bg-[#0a1128] p-6 rounded-xl border border-slate-800 shadow-xl">
          <span className="text-xs text-slate-400 font-bold block uppercase">
            ENGINE TIMEOUT COOLDOWN
          </span>
          <h2 className="text-3xl font-black text-amber-400 mt-1">
            {Math.floor(timeRemaining / 3600)
              .toString()
              .padStart(2, '0')}
            :
            {Math.floor((timeRemaining % 3600) / 60)
              .toString()
              .padStart(2, '0')}
            :{(timeRemaining % 60).toString().padStart(2, '0')}
          </h2>
          <span className="text-xs text-slate-500 block mt-0.5">
            Absolute Force Liquidate Threshold Guard Window
          </span>
        </div>
      </div>

      {subAgents.length > 0 && (
        <div className="mb-6 bg-slate-950 p-6 rounded-xl border border-amber-500/20">
          <h3 className="text-sm font-black text-amber-400 tracking-wider uppercase mb-4 flex items-center gap-2">
            <GitFork className="w-4 h-4" /> Active Sub-Agent Fleet Matrix (Recursive Mitosis Engaged)
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {subAgents.map((agent) => (
              <div
                key={agent.id}
                className="bg-[#0a1128] p-3 rounded-lg border border-slate-800 flex flex-col justify-between"
              >
                <span className="text-xs font-black text-white mb-1">{agent.id}</span>
                <p className="text-[10px] text-slate-500 truncate font-mono mb-2">{agent.pubkey}</p>
                <div className="flex justify-between items-center text-[10px] bg-slate-950 p-2 rounded border border-slate-900">
                  <span className="text-slate-400">
                    Allocated: <b className="text-white">${agent.balanceUsd.toFixed(2)}</b>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-[#0a1128] rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-slate-800 bg-[#0e1735] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-teal-400" />
            <h3 className="text-xs font-black text-white uppercase tracking-wider">
              On-Chain Transaction Action Ledger (0.001 SOL Size)
            </h3>
          </div>
        </div>
        <div className="p-4 overflow-x-auto">
          {liveTransactions.length === 0 ? (
            <div className="h-32 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
              Waiting for live transaction confirmation signatures from the Jupiter execution routing
              daemon...
            </div>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-2">Signature hash</th>
                  <th className="pb-2">Direction</th>
                  <th className="pb-2">Asset size</th>
                  <th className="pb-2">Slot height</th>
                </tr>
              </thead>
              <tbody>
                {liveTransactions.map((tx) => (
                  <tr key={tx.signature} className="border-b border-slate-900">
                    <td className="py-2 text-teal-400 select-all">{tx.signature}</td>
                    <td
                      className={`py-2 font-bold ${
                        tx.direction === 'BUY' ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {tx.direction}
                    </td>
                    <td className="py-2">{tx.amountSol} SOL</td>
                    <td className="py-2 text-slate-400">{tx.slot}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
