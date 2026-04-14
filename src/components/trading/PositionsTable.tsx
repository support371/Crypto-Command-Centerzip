'use client';

import { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';

interface Position {
  id: string;
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  exchange: string;
  opened_at: string;
}

export default function PositionsTable() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPositions() {
      try {
        const res = await fetch('/api/positions');
        if (res.ok) {
          const data = await res.json();
          setPositions(data.positions || []);
        }
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    }
    fetchPositions();
    const interval = setInterval(fetchPositions, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-surface-card border border-surface-border rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-surface-border">
        <h2 className="font-semibold text-white">Open Positions</h2>
        <div className="flex items-center gap-2 text-xs text-surface-muted">
          <RefreshCw className="w-3 h-3" />
          Live
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-surface-muted uppercase border-b border-surface-border">
              <th className="text-left px-5 py-3">Symbol</th>
              <th className="text-left px-5 py-3">Side</th>
              <th className="text-right px-5 py-3">Size</th>
              <th className="text-right px-5 py-3">Entry</th>
              <th className="text-right px-5 py-3">Current</th>
              <th className="text-right px-5 py-3">Unr. PnL</th>
              <th className="text-left px-5 py-3">Exchange</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="text-center py-10 text-surface-muted">Loading positions...</td>
              </tr>
            ) : positions.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-10 text-surface-muted">
                  No open positions
                </td>
              </tr>
            ) : (
              positions.map((pos) => (
                <tr key={pos.id} className="border-b border-surface-border/50 hover:bg-surface/50 transition-colors">
                  <td className="px-5 py-3 font-mono font-semibold text-white">{pos.symbol}</td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                      pos.side === 'long' ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'
                    }`}>
                      {pos.side.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-right font-mono text-white">{pos.size}</td>
                  <td className="px-5 py-3 text-right font-mono text-white">${pos.entry_price.toLocaleString()}</td>
                  <td className="px-5 py-3 text-right font-mono text-white">${pos.current_price.toLocaleString()}</td>
                  <td className={`px-5 py-3 text-right font-mono font-semibold ${
                    pos.unrealized_pnl >= 0 ? 'text-success' : 'text-danger'
                  }`}>
                    {pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl.toFixed(2)}
                    <span className="text-xs ml-1 opacity-70">
                      ({pos.unrealized_pnl_pct >= 0 ? '+' : ''}{pos.unrealized_pnl_pct.toFixed(2)}%)
                    </span>
                  </td>
                  <td className="px-5 py-3 text-surface-muted text-xs uppercase">{pos.exchange}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
