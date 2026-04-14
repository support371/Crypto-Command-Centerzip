'use client';

import { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldOff } from 'lucide-react';

type GuardianState = 'active' | 'triggered' | 'killed' | 'offline';

export default function GuardianStatus() {
  const [state, setState] = useState<GuardianState>('offline');

  useEffect(() => {
    async function fetchStatus() {
      try {
        const res = await fetch('/api/guardian/status');
        if (res.ok) {
          const data = await res.json();
          setState(data.state || 'offline');
        }
      } catch {
        setState('offline');
      }
    }
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const config = {
    active: { icon: Shield, label: 'Guardian Active', className: 'text-brand-400 bg-brand-600/10 border-brand-600/30' },
    triggered: { icon: ShieldAlert, label: 'Guardian Triggered', className: 'text-warning bg-warning/10 border-warning/30 animate-pulse' },
    killed: { icon: ShieldOff, label: 'KILL SWITCH ACTIVE', className: 'text-danger bg-danger/10 border-danger/30 animate-pulse' },
    offline: { icon: Shield, label: 'Guardian Offline', className: 'text-surface-muted bg-surface border-surface-border' },
  }[state];

  const Icon = config.icon;

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium ${config.className}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{config.label}</span>
    </div>
  );
}
