import { useMemo } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";

export function PriceChart({ seed }: { seed: number }) {
  const data = useMemo(() => {
    const rows = [];
    let v = 148;
    for (let i = 0; i < 48; i++) {
      v += Math.sin((i + seed) / 4) * 1.4 + Math.cos((i + seed) / 9) * 0.6;
      rows.push({ h: `${String(i).padStart(2, "0")}`, px: Math.round(v * 100) / 100 });
    }
    return rows;
  }, [seed]);

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="miraFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2ee6a6" stopOpacity={0.5} />
              <stop offset="40%" stopColor="#2ee6a6" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#2ee6a6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="miraStroke" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#2ee6a6" />
              <stop offset="50%" stopColor="#4fffd4" />
              <stop offset="100%" stopColor="#2ee6a6" />
            </linearGradient>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1a1f26" opacity={0.4} />
          <XAxis dataKey="h" hide />
          <YAxis domain={["auto", "auto"]} hide />
          <Tooltip
            contentStyle={{
              background: "rgba(12, 16, 22, 0.95)",
              border: "1px solid rgba(46, 230, 166, 0.4)",
              borderRadius: 12,
              fontSize: 12,
              backdropFilter: "blur(12px)",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.5)",
            }}
            itemStyle={{ color: "#e8eef5" }}
            labelStyle={{ color: "#7d8794" }}
          />
          <Area
            type="monotone"
            dataKey="px"
            stroke="url(#miraStroke)"
            fill="url(#miraFill)"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 5, fill: "#2ee6a6", stroke: "#4fffd4", strokeWidth: 2, filter: "url(#glow)" }}
            style={{ filter: "url(#glow)" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
