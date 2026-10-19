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
              <stop offset="0%" stopColor="#2ee6a6" stopOpacity={0.4} />
              <stop offset="50%" stopColor="#2ee6a6" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#2ee6a6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="miraStroke" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#2ee6a6" />
              <stop offset="100%" stopColor="#4fffd4" />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#24302a" opacity={0.3} />
          <XAxis dataKey="h" hide />
          <YAxis domain={["auto", "auto"]} hide />
          <Tooltip
            contentStyle={{
              background: "rgba(16, 21, 28, 0.95)",
              border: "1px solid rgba(46, 230, 166, 0.3)",
              borderRadius: 12,
              fontSize: 12,
              backdropFilter: "blur(8px)",
              boxShadow: "0 4px 20px rgba(0, 0, 0, 0.3)",
            }}
            itemStyle={{ color: "#e7efe8" }}
            labelStyle={{ color: "#8b978f" }}
          />
          <Area
            type="monotone"
            dataKey="px"
            stroke="url(#miraStroke)"
            fill="url(#miraFill)"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 4, fill: "#2ee6a6", stroke: "#4fffd4", strokeWidth: 2 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
