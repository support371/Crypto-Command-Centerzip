'use client';

import { useState, useEffect, useRef } from 'react';
import Sidebar from '@/components/ui/Sidebar';
import { Terminal, Send, AlertTriangle, ShieldOff } from 'lucide-react';

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'success';
  source: string;
  message: string;
}

export default function CommandCenterPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [killConfirm, setKillConfirm] = useState(false);
  const [killing, setKilling] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function fetchLogs() {
      try {
        const res = await fetch('/api/audit/logs?limit=50');
        if (res.ok) {
          const data = await res.json();
          setLogs(data.logs || []);
          logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
      } catch {}
    }
    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, []);

  async function triggerKillSwitch() {
    if (!killConfirm) { setKillConfirm(true); return; }
    setKilling(true);
    try {
      await fetch('/api/guardian/kill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: 'manual_ui_trigger' }),
      });
    } catch {}
    setKilling(false);
    setKillConfirm(false);
  }

  const levelColor = (l: LogEntry['level']) => ({
    info: 'text-slate-400',
    warn: 'text-warning',
    error: 'text-danger',
    success: 'text-success',
  }[l]);

  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <main className="flex-1 p-6 overflow-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Terminal className="w-6 h-6 text-brand-400" />
              Command Center
            </h1>
            <p className="text-surface-muted text-sm mt-0.5">Live system audit log & controls</p>
          </div>
          <button
            onClick={triggerKillSwitch}
            disabled={killing}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
              killConfirm
                ? 'bg-danger text-white animate-pulse'
                : 'bg-danger/10 border border-danger/30 text-danger hover:bg-danger/20'
            }`}
          >
            <ShieldOff className="w-4 h-4" />
            {killing ? 'Executing...' : killConfirm ? 'CONFIRM KILL SWITCH' : 'Kill Switch'}
          </button>
        </div>

        {killConfirm && !killing && (
          <div className="mb-4 p-4 bg-danger/10 border border-danger/30 rounded-xl flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-danger shrink-0" />
            <p className="text-sm text-danger">
              This will immediately close ALL positions and halt all trading. Click again to confirm.
              <button onClick={() => setKillConfirm(false)} className="ml-3 text-surface-muted hover:text-white underline">
                Cancel
              </button>
            </p>
          </div>
        )}

        {/* Audit log terminal */}
        <div className="bg-surface-card border border-surface-border rounded-xl overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-surface-border bg-surface">
            <div className="w-3 h-3 rounded-full bg-danger/60" />
            <div className="w-3 h-3 rounded-full bg-warning/60" />
            <div className="w-3 h-3 rounded-full bg-success/60" />
            <span className="text-xs text-surface-muted ml-2 font-mono">audit.log — live stream</span>
          </div>
          <div className="h-[60vh] overflow-y-auto p-4 font-mono text-sm space-y-1 bg-surface">
            {logs.length === 0 ? (
              <p className="text-surface-muted">Waiting for audit events...</p>
            ) : (
              logs.map((log) => (
                <div key={log.id} className="flex gap-3">
                  <span className="text-surface-muted shrink-0">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="text-slate-500 uppercase text-xs shrink-0 w-12">[{log.source}]</span>
                  <span className={`${levelColor(log.level)} text-xs uppercase font-semibold shrink-0 w-10`}>
                    {log.level}
                  </span>
                  <span className="text-slate-300">{log.message}</span>
                </div>
              ))
            )}
            <div ref={logsEndRef} />
          </div>
        </div>
      </main>
    </div>
  );
}
