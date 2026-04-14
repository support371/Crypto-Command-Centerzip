'use client';

import { useState, useEffect, useRef } from 'react';
import { Zap, TrendingUp, TrendingDown } from 'lucide-react';

interface Signal {
  id: string;
  symbol: string;
  direction: 'long' | 'short';
  strength: number;
  source: string;
  timestamp: string;
  status: 'pending' | 'executed' | 'rejected' | 'expired';
}

export default function SignalFeed() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function fetchSignals() {
      try {
        const res = await fetch('/api/signals/recent?limit=20');
        if (res.ok) {
          const data = await res.json();
          setSignals(data.signals || []);
        }
      } catch {
        // silent
      }
    }
    fetchSignals();
    const interval = setInterval(fetchSignals, 2000);
    return () => clearInterval(interval);
  }, []);

  const statusColor = (s: Signal['status']) => ({
    pending: 'text-warning',
    executed: 'text-success',
    rejected: 'text-danger',
    expired: 'text-surface-muted',
  }[s]);

  return (
    <div className="bg-surface-card border border-surface-border rounded-xl h-full flex flex-col">
      <div className="flex items-center justify-between px-5 py-4 border-b border-surface-border">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-brand-400" />
          <h2 className="font-semibold text-white">Signal Feed</h2>
        </div>
        <span className="text-xs text-surface-muted">{signals.length} recent</span>
      </div>
      <div ref={listRef} className="flex-1 overflow-y-auto p-3 space-y-2">
        {signals.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full py-8 text-surface-muted">
            <Zap className="w-6 h-6 mb-2 opacity-40" />
            <p className="text-sm">Waiting for signals...</p>
          </div>
        ) : (
          signals.map((sig) => (
            <div key={sig.id} className="flex items-start gap-3 p-3 bg-surface rounded-lg border border-surface-border/50">
              <div className={`mt-0.5 p-1 rounded ${sig.direction === 'long' ? 'bg-success/10' : 'bg-danger/10'}`}>
                {sig.direction === 'long'
                  ? <TrendingUp className="w-3 h-3 text-success" />
                  : <TrendingDown className="w-3 h-3 text-danger" />
                }
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-semibold text-white text-sm">{sig.symbol}</span>
                  <span className={`text-xs font-medium ${statusColor(sig.status)}`}>
                    {sig.status}
                  </span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex-1 bg-surface-border rounded-full h-1">
                    <div
                      className={`h-1 rounded-full ${sig.direction === 'long' ? 'bg-success' : 'bg-danger'}`}
                      style={{ width: `${sig.strength * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-surface-muted">{(sig.strength * 100).toFixed(0)}%</span>
                </div>
                <p className="text-xs text-surface-muted mt-1">
                  {sig.source} · {new Date(sig.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
