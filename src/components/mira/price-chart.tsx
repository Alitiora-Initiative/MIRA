import { useMemo } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

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
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="miraFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2ee6a6" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#2ee6a6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="h" hide />
          <YAxis domain={["auto", "auto"]} hide />
          <Tooltip
            contentStyle={{
              background: "#10151c",
              border: "1px solid #24302a",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Area type="monotone" dataKey="px" stroke="#2ee6a6" fill="url(#miraFill)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
