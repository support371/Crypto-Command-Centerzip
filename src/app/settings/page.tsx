'use client';

import { useState } from 'react';
import Sidebar from '@/components/ui/Sidebar';
import { Settings, Shield, AlertTriangle, Save } from 'lucide-react';

export default function SettingsPage() {
  const [riskLimits, setRiskLimits] = useState({
    maxPositionSizeUsd: 10000,
    maxDailyLossUsd: 500,
    maxOpenPositions: 10,
    autoKillDrawdownPct: 5.0,
    autoKillLossUsd: 1000.0,
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  async function handleSave() {
    setSaving(true);
    try {
      await fetch('/api/settings/risk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(riskLimits),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <main className="flex-1 p-6 overflow-auto max-w-3xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Settings className="w-6 h-6 text-brand-400" />
            Settings
          </h1>
          <p className="text-surface-muted text-sm mt-0.5">Risk configuration and system preferences</p>
        </div>

        {/* Risk Limits */}
        <div className="bg-surface-card border border-surface-border rounded-xl p-6 mb-6">
          <div className="flex items-center gap-2 mb-5">
            <Shield className="w-5 h-5 text-brand-400" />
            <h2 className="font-semibold text-white">Risk Limits</h2>
          </div>
          <div className="grid grid-cols-1 gap-4">
            {[
              { key: 'maxPositionSizeUsd', label: 'Max Position Size (USD)', min: 100, max: 1000000, step: 100 },
              { key: 'maxDailyLossUsd', label: 'Max Daily Loss (USD)', min: 50, max: 100000, step: 50 },
              { key: 'maxOpenPositions', label: 'Max Open Positions', min: 1, max: 50, step: 1 },
              { key: 'autoKillDrawdownPct', label: 'Auto Kill-Switch Drawdown (%)', min: 1, max: 50, step: 0.5 },
              { key: 'autoKillLossUsd', label: 'Auto Kill-Switch Loss (USD)', min: 100, max: 100000, step: 100 },
            ].map(({ key, label, min, max, step }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">{label}</label>
                <input
                  type="number"
                  min={min}
                  max={max}
                  step={step}
                  value={riskLimits[key as keyof typeof riskLimits]}
                  onChange={(e) => setRiskLimits(prev => ({ ...prev, [key]: parseFloat(e.target.value) }))}
                  className="w-full bg-surface border border-surface-border rounded-lg px-4 py-2.5 text-white font-mono focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Warning */}
        <div className="bg-warning/5 border border-warning/20 rounded-xl p-4 mb-6 flex items-start gap-3">
          <AlertTriangle className="w-4 h-4 text-warning mt-0.5 shrink-0" />
          <p className="text-sm text-warning/80">
            Risk limits take effect immediately on save. Guardian bot has absolute override authority and will enforce
            these limits regardless of pending orders.
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-6 py-2.5 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-semibold rounded-lg transition-colors"
        >
          <Save className="w-4 h-4" />
          {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Settings'}
        </button>
      </main>
    </div>
  );
}
