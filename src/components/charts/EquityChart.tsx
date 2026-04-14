'use client';

import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

interface EquityPoint {
  timestamp: string;
  equity: number;
  balance: number;
}

export default function EquityChart() {
  const [data, setData] = useState<EquityPoint[]>([]);
  const [period, setPeriod] = useState<'1D' | '1W' | '1M'>('1D');

  useEffect(() => {
    async function fetchEquity() {
      try {
        const res = await fetch(`/api/account/equity-history?period=${period}`);
        if (res.ok) {
          const d = await res.json();
          setData(d.data || []);
        }
      } catch {
        // silent
      }
    }
    fetchEquity();
  }, [period]);

  const isPositive = data.length < 2 || data[data.length - 1]?.equity >= data[0]?.equity;

  return (
    <div className="bg-surface-card border border-surface-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-white">Equity Curve</h2>
        <div className="flex rounded-lg bg-surface border border-surface-border p-0.5 gap-0.5">
          {(['1D', '1W', '1M'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                period === p ? 'bg-brand-600 text-white' : 'text-surface-muted hover:text-white'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>
      <div className="h-48">
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-surface-muted text-sm">
            No equity data yet — start trading to see the curve
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
              <defs>
                <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={isPositive ? '#22c55e' : '#ef4444'} stopOpacity={0.15} />
                  <stop offset="95%" stopColor={isPositive ? '#22c55e' : '#ef4444'} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(v) => format(new Date(v), 'HH:mm')}
                stroke="#475569"
                tick={{ fontSize: 11 }}
              />
              <YAxis
                stroke="#475569"
                tick={{ fontSize: 11 }}
                tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`}
                width={52}
              />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelFormatter={(v) => format(new Date(v), 'MMM d HH:mm')}
                formatter={(v: number) => [`$${v.toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Equity']}
              />
              <Area
                type="monotone"
                dataKey="equity"
                stroke={isPositive ? '#22c55e' : '#ef4444'}
                strokeWidth={2}
                fill="url(#equityGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
